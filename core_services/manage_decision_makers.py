import streamlit as st
import psycopg2
from connect import get_connection
import pandas as pd

def render_manage_decision_makers():
    st.title("👤 Управление базой ЛПРов")

    # Функция добавления ЛПР
    def add_dm(last_name, first_name, middle_name, age):
        if not last_name or not first_name or not age:
            st.warning("Пожалуйста, заполните все обязательные поля (фамилия, имя, возраст).")
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO decision_makers (last_name, first_name, middle_name, age) VALUES (%s, %s, %s, %s)",
                    (last_name, first_name, middle_name, age)
                )
                conn.commit()
                st.success("ЛПР добавлен.")

    # Функция изменения ЛПР
    def update_dm(dm_id, last_name, first_name, middle_name, age):
        if not last_name or not first_name or not age:
            st.warning("Пожалуйста, заполните все обязательные поля (фамилия, имя, возраст).")
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM decision_makers WHERE dm_id = %s", (dm_id,))
                if not cur.fetchone():
                    st.error("ЛПР с таким ID не найден.")
                    return
                cur.execute(
                    "UPDATE decision_makers SET last_name = %s, first_name = %s, middle_name = %s, age = %s WHERE dm_id = %s",
                    (last_name, first_name, middle_name, age, dm_id)
                )
                conn.commit()
                st.success("ЛПР обновлен.")

    # Функция удаления ЛПР
    def delete_dm(dm_id: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM decision_makers WHERE dm_id = %s", (dm_id,))
                if not cur.fetchone():
                    st.error("ЛПР с таким ID не найден.")
                    return
                try:
                    cur.execute("DELETE FROM decision_makers WHERE dm_id = %s", (dm_id,))
                    conn.commit()
                    st.success("ЛПР удалён.")
                except psycopg2.errors.ForeignKeyViolation:
                    conn.rollback()
                    st.error("Невозможно удалить ЛПР, закреплённого за поставщиком. "
                            "Рекомендуем сначала изменить ЛПРа у поставщика или удалить самого поставщика.")


    # Функция выгрузки всех ЛПР
    def view_decision_makers():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT last_name, first_name, middle_name, age FROM decision_makers")
                rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=["Фамилия", "Имя", "Отчество", "Возраст"])
        st.dataframe(df, use_container_width=True)

    # UI для управления ЛПР
    action = st.selectbox("Выберите действие", ["Посмотреть всех ЛПР", "Добавить ЛПР", "Изменить ЛПР", "Удалить ЛПР"])

    if action == "Посмотреть всех ЛПР":
        view_decision_makers()

    elif action == "Добавить ЛПР":
        last_name = st.text_input("Фамилия")
        first_name = st.text_input("Имя")
        middle_name = st.text_input("Отчество")
        age = st.number_input("Возраст", min_value=18, max_value=100)
        if st.button("Добавить"):
            add_dm(last_name, first_name, middle_name, age)

    elif action == "Изменить ЛПР":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT dm_id, last_name, first_name, middle_name, age FROM decision_makers")
                dms = cur.fetchall()

        if not dms:
            st.info("Нет доступных ЛПР для изменения.")
            return

        dm_map = {f"{d[1]} {d[2]} {d[3]}, {d[4]} лет": d[0] for d in dms}
        selected = st.selectbox("Выберите ЛПР", list(dm_map.keys()))
        dm_id = dm_map[selected]

        last_name = st.text_input("Новая фамилия")
        first_name = st.text_input("Новое имя")
        middle_name = st.text_input("Новое отчество")
        age = st.number_input("Новый возраст", min_value=18, max_value=100)
        if st.button("Изменить"):
            update_dm(dm_id, last_name, first_name, middle_name, age)


    elif action == "Удалить ЛПР":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT dm_id, last_name, first_name, middle_name, age FROM decision_makers")
                dms = cur.fetchall()

        if not dms:
            st.info("Нет доступных ЛПР для удаления.")
            return

        dm_map = {f"{d[1]} {d[2]} {d[3]}, {d[4]} лет": d[0] for d in dms}
        selected = st.selectbox("Выберите ЛПР для удаления", list(dm_map.keys()))
        dm_id = dm_map[selected]

        if st.button("Удалить"):
            delete_dm(dm_id)
