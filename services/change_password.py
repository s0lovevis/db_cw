import streamlit as st
from connect import get_connection

def render_change_password():
    st.title("🔐 Смена пароля")

    current_password = st.text_input("Текущий пароль", type="password")
    new_password = st.text_input("Новый пароль", type="password")

    if st.button("Сменить пароль"):
        if not current_password or not new_password:
            st.warning("Пожалуйста, заполните все поля.")
            return

        with st.spinner("Обновление пароля..."):
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 1 FROM users 
                        WHERE username = %s AND password_hash = crypt(%s, password_hash)
                        """,
                        (st.session_state.username, current_password)
                    )
                    if not cur.fetchone():
                        st.error("Неверный текущий пароль.")
                        return

                    cur.execute(
                        """
                        UPDATE users 
                        SET password_hash = crypt(%s, gen_salt('bf'))
                        WHERE username = %s
                        """,
                        (new_password, st.session_state.username)
                    )
                    conn.commit()
                    st.success("Пароль успешно обновлён.")
