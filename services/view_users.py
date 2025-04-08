import streamlit as st
from connect import get_connection
import pandas as pd

def render_view_users():
    st.title("📋 Просмотр списка сотрудников")

    filter_option = st.radio(
        "Каких сотрудников вы хотите выгрузить:",
        ["Администратор CRM-системы", "Менеджер по работе с поставщиками", "Сотрудник склада", "Всех сотрудников"]
    )

    if st.button("Сделать выгрузку"):
        with st.spinner("Получение данных..."):
            query = """
                SELECT u.username, r.description AS role_description
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
            """

            filters = {
                "Администратор CRM-системы": "WHERE r.name = 'admin'",
                "Менеджер по работе с поставщиками": "WHERE r.name = 'manager'",
                "Сотрудник склада": "WHERE r.name = 'warehouse_worker'",
                "Всех сотрудников": ""
            }

            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query + " " + filters[filter_option])
                    rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=["Логин", "Роль"])
            st.dataframe(df, use_container_width=True)
