import streamlit as st
from connect import get_connection

def render_add_user_form():
    st.title("👥 Добавление нового пользователя")

    username = st.text_input("Введите логин")
    password = st.text_input("Введите пароль", type="password")
    role = st.selectbox("Выберите роль", ["admin", "manager", "warehouse_worker"])

    if st.button("Добавить пользователя"):
        if not username or not password:
            st.warning("Пожалуйста, заполните все поля.")
            return

        with st.spinner("Добавление пользователя..."):
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
                    if cur.fetchone():
                        st.error("Пользователь с таким логином уже существует.")
                        return

                    cur.execute("SELECT role_id FROM roles WHERE name = %s", (role,))
                    result = cur.fetchone()
                    if not result:
                        st.error("Ошибка: не найдена роль.")
                        return
                    role_id = result[0]

                    cur.execute(
                        "INSERT INTO users (username, password_hash, role_id) "
                        "VALUES (%s, crypt(%s, gen_salt('bf')), %s)",
                        (username, password, role_id)
                    )
                    conn.commit()
                    st.success(f"Пользователь {username} успешно добавлен.")
