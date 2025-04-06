import streamlit as st
from services.auth_service import authenticate_user
from services.access_service import get_access_rights_by_role
from services.add_new_user import render_add_user_form
from services.change_password import render_change_password
from services.delete_user import render_delete_user
from services.view_users import render_view_users


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
            with st.spinner("⏳ Поиск пользователя ..."):
                result = authenticate_user(username, password)
                if result:
                    uname, role, role_desc = result
                    rights = get_access_rights_by_role(role)

                    st.session_state.username = uname
                    st.session_state.role = role
                    st.session_state.role_desc = role_desc
                    st.session_state.access_rights = rights
                    st.session_state.current_state = "welcome"
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")

def show_sidebar():
    st.sidebar.markdown(f"👤 Вы вошли под логином: **{st.session_state.username}**")
    st.sidebar.markdown(f"🔑 Ваша роль: **{st.session_state.role_desc}**")
    st.sidebar.markdown("---")

    pages = {description: name for name, description in st.session_state.access_rights}

    selection_description = st.sidebar.radio(
        "📂 Разделы",
        ["Главная"] + list(pages.keys())
    )

    # Преобразуем обратно в name
    selection = "welcome" if selection_description == "Главная" else pages[selection_description]
    st.session_state.current_state = selection

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Выйти"):
        logout()

def show_welcome():
    st.title("Добрый день!")
    st.markdown(f"""
    В меню слева выберите действие, которое хотите выполнить.
    """)

def show_dynamic_page():
    current = st.session_state.current_state
    if current == "add_new_user":
        render_add_user_form()
    elif current == "change_password":
        render_change_password()
    elif current == "delete_user":
        render_delete_user()
    elif current == "view_users":
        render_view_users()
    else:
        st.title(f"📄 Раздел: {current}")
        st.write("Здесь будет функциональность, связанная с этим доступом.")



def main():
    st.set_page_config(page_title="SRM-система", page_icon="📦")

    if "current_state" not in st.session_state:
        st.session_state.current_state = "login"
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.access_rights = []

    if st.session_state.current_state == "login":
        show_login()
    else:
        show_sidebar()
        if st.session_state.current_state == "welcome":
            show_welcome()
        else:
            show_dynamic_page()

if __name__ == "__main__":
    main()
