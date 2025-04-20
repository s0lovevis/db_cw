import streamlit as st
from connect import get_connection

def render_view_warehouse():
    st.title("📦 Просмотр товаров на складе")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                       c.name       AS item_name,
                       s.company_name,
                       w.quantity
                FROM warehouse w
                JOIN catalog c ON w.item_id = c.item_id
                JOIN suppliers s ON c.supplier_id = s.supplier_id
                WHERE w.quantity > 0
                ORDER BY c.name
            """)
            rows = cur.fetchall()

    if not rows:
        st.info("На складе нет доступных товаров.")
        return

    # Выводим табличку
    headers = ['Название', 'Поставщик', 'Количество']
    data = [row for row in rows]
    st.table([dict(zip(headers, r)) for r in data])