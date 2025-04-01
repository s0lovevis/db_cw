import streamlit as st
from services.auth_service import authenticate_user
from services.access_service import get_access_rights_by_role

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.current_state = "login"
    st.rerun()

def show_login():
    st.title("🔐 SRM-система — Вход")
    with st.form("login_form"):
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Войти")

        if submitted:
            result = authenticate_user(username, password)
            if result:
                uname, role = result
                rights = get_access_rights_by_role(role)

                st.session_state.username = uname
                st.session_state.role = role
                st.session_state.access_rights = rights
                st.session_state.current_state = "main"
                st.rerun()
            else:
                st.error("Неверный логин или пароль")

def show_main():
    st.title("📦 SRM-система")
    st.success(f"Привет, {st.session_state.username}! Твоя роль — {st.session_state.role}")
    st.write("### 🧾 Твои доступы:")

    if st.session_state.access_rights:
        for name, description in st.session_state.access_rights:
            st.markdown(f"- **{name}** — {description}")
    else:
        st.info("Нет доступов для твоей роли.")

    if st.button("🚪 Выйти"):
        logout()

def main():
    st.set_page_config(page_title="SRM-система", page_icon="📦")

    if "current_state" not in st.session_state:
        st.session_state.current_state = "login"
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.access_rights = []

    if st.session_state.current_state == "login":
        show_login()
    elif st.session_state.current_state == "main":
        show_main()

if __name__ == "__main__":
    main()
