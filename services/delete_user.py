import streamlit as st
from connect import get_connection

def render_delete_user():
    st.title("🗑️ Удаление пользователя")

    username = st.text_input("Введите логин пользователя, которого хотите удалить")
    confirm = st.checkbox("Вы уверены, что хотите удалить юзера?")

    if st.button("Удалить пользователя"):
        if not username:
            st.warning("Введите логин пользователя.")
            return
        if not confirm:
            st.warning("Подтвердите удаление, поставив галочку.")
            return

        with st.spinner("Удаление пользователя..."):
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Проверка: существует ли пользователь и не admin ли он
                    cur.execute("""
                        SELECT r.name
                        FROM users u
                        JOIN roles r ON u.role_id = r.role_id
                        WHERE u.username = %s
                    """, (username,))
                    result = cur.fetchone()

                    if not result:
                        st.error("Пользователь с таким логином не найден.")
                        return
                    if result[0] == "admin":
                        st.error("Нельзя удалить пользователя с ролью 'admin'.")
                        return

                    # Удаляем пользователя
                    cur.execute("DELETE FROM users WHERE username = %s", (username,))
                    conn.commit()
                    st.success(f"Пользователь {username} успешно удалён.")
