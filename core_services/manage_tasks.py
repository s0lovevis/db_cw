import streamlit as st
from connect import get_connection, get_redis_connection
import json, uuid, datetime

# Основная отрисовка страницы управления заданиями
def render_manage_tasks():
    st.title("📋 Панель работы с заданиями")
    tabs = st.tabs(["Создать задание", "Мои задания", "Все задания"])
    with tabs[0]: create_task_form()
    with tabs[1]: show_my_tasks()
    with tabs[2]: show_all_tasks()

# Форма создания нового задания
def create_task_form():
    st.subheader("Создание нового задания")
    types = load_task_types()
    users = load_users_for_assignment()
    if not types or not users:
        st.info("Недостаточно данных для создания задания.")
        return

    type_choice = st.selectbox("Тип задания", [t['name_ru'] for t in types])
    selected_type = next(t for t in types if t['name_ru']==type_choice)

    assignee = st.selectbox(
        "Назначить пользователю", [u['username'] for u in users]
    )
    description = st.text_area("Описание задания", height=100)

    if st.button("Создать"):  
        if not description:
            st.warning("Описание не может быть пустым.")
            return
        create_task(selected_type['type_id'], assignee, description)
        st.success("Задание создано!")

# Отображение личных заданий
def show_my_tasks():
    user = st.session_state.username
    tabs = st.tabs(["Назначенные мне", "Созданные мной"])
    with tabs[0]: render_task_list(get_tasks('assignee', user), is_assignee=True)
    with tabs[1]: render_task_list(get_tasks('creator', user), is_assignee=False)

# Отображение всех заданий (только для админа)
def show_all_tasks():
    if st.session_state.role != 'admin':
        st.info("Только администратор может просматривать все задания.")
        return
    render_task_list(get_tasks('all'), is_assignee=False)

# Вспомогательная функция рендеринга списка заданий
def render_task_list(tasks, is_assignee=False):
    if not tasks:
        st.info("Заданий нет.")
        return
    for task in tasks:
        created = task['created_at'].strftime('%d.%m.%Y %H:%M')
        status = 'Завершено' if task['completed_at'] else 'В процессе'
        with st.expander(f"{task['type_name']} ({created}) — {status}"):
            st.write(f"**Описание:** {task['description']}")
            st.write(f"**Создатель:** {task['creator_username']}")
            st.write(f"**Исполнитель:** {task['assignee_username']}")
            if is_assignee and not task['completed_at']:
                if st.button("Завершить задание", key=f"complete_{task['task_id']}"):
                    complete_task(task['task_id'])
                    st.success("Задание завершено!")
                    st.rerun()

# Загрузка типов заданий из БД
def load_task_types():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT type_id, name_ru FROM task_types")
        return [{'type_id': t[0], 'name_ru': t[1]} for t in cur.fetchall()]

# Загрузка пользователей для назначения заданий с новой логикой
def load_users_for_assignment():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT u.username, r.name FROM users u JOIN roles r ON u.role_id=r.role_id"
        )
        rows = cur.fetchall()
    role = st.session_state.role
    me = st.session_state.username
    if role == 'admin':
        # Админ может назначать на менеджеров и сотрудников склада
        return [{'username': u[0]} for u in rows if u[1] in ('manager', 'warehouse_worker')]
    elif role in ('manager', 'warehouse_worker'):
        # Менеджер и склад могут назначать на всех кроме админа
        return [{'username': u[0]} for u in rows if u[1] != 'admin']
    return []

# Создание задания: запись в Postgres и Redis
def create_task(type_id, assignee, description):
    creator = st.session_state.username
    now_iso = datetime.datetime.utcnow().isoformat()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (type_id, creator_username, assignee_username) VALUES (%s,%s,%s) RETURNING task_id",
            (type_id, creator, assignee)
        )
        db_id = cur.fetchone()[0]
        conn.commit()
    r = get_redis_connection()
    key = f"task:{db_id}"
    data = {
        'task_id': db_id,
        'type_id': type_id,
        'type_name': next(t['name_ru'] for t in load_task_types() if t['type_id']==type_id),
        'creator_username': creator,
        'assignee_username': assignee,
        'description': description,
        'created_at': now_iso,
        'completed_at': None
    }
    payload = json.dumps(data)
    r.set(key, payload)
    r.sadd(f"user:{creator}:created", db_id)
    r.sadd(f"user:{assignee}:assigned", db_id)
    r.sadd("tasks:all", db_id)

# Отметка задания как завершенного: обновление в БД и Redis
def complete_task(task_id):
    now_iso = datetime.datetime.utcnow().isoformat()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET completed_at=NOW() WHERE task_id=%s", (task_id,))
        conn.commit()
    r = get_redis_connection()
    key = f"task:{task_id}"
    data = json.loads(r.get(key))
    data['completed_at'] = now_iso
    r.set(key, json.dumps(data))

# Получение списка заданий из Redis
def get_tasks(mode, username=None):
    r = get_redis_connection()
    if mode == 'assignee':
        ids = r.smembers(f"user:{username}:assigned")
    elif mode == 'creator':
        ids = r.smembers(f"user:{username}:created")
    else:
        ids = r.smembers("tasks:all")
    tasks = []
    for tid in ids:
        tid = tid.decode() if isinstance(tid, bytes) else tid
        raw = r.get(f"task:{tid}")
        if not raw:
            continue
        task = json.loads(raw)
        task['created_at'] = datetime.datetime.fromisoformat(task['created_at'])
        if task['completed_at']:
            task['completed_at'] = datetime.datetime.fromisoformat(task['completed_at'])
        tasks.append(task)
    return sorted(tasks, key=lambda x: x['created_at'], reverse=True)
