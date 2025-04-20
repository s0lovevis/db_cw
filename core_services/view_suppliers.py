import streamlit as st
import pandas as pd
from connect import get_connection

def render_view_suppliers():
    st.title("💼 Просмотр базы поставщиков")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    s.company_name, s.inn,
                    la.city, la.street, la.house, la.building,
                    dm.last_name, dm.first_name, dm.middle_name, dm.age
                FROM suppliers s
                JOIN legal_addresses la ON s.address_id = la.address_id
                JOIN decision_makers dm ON s.dm_id = dm.dm_id
            """)
            rows = cur.fetchall()

    if not rows:
        st.info("В системе пока нет поставщиков")
        return

    df = pd.DataFrame(rows, columns=[
        "Название компании", "ИНН",
        "Город", "Улица", "Дом", "Строение",
        "Фамилия ЛПР", "Имя ЛПР", "Отчество ЛПР", "Возраст ЛПР"
    ])
    st.dataframe(df, use_container_width=True)