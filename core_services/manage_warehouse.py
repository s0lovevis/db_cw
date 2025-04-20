import streamlit as st
from connect import get_connection

def render_manage_warehouse():
    st.title("🏭 Управление складом")

    # 1) Получаем список товаров из каталога
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.item_id, c.name, s.company_name
                FROM catalog c
                JOIN suppliers s ON c.supplier_id = s.supplier_id
            """)
            rows = cur.fetchall()
    if not rows:
        st.info("Каталог пуст.")
        return

    # 2) Формируем отображение "Товар [name] от поставщика [supplier]"
    item_map = {
        f"Товар «{item_name}» от «{supplier_name}»": item_id
        for item_id, item_name, supplier_name in rows
    }
    selection = st.selectbox("Выберите товар", list(item_map.keys()))
    item_id = item_map[selection]

    # 3) Операция: Добавить/Удалить
    operation = st.radio("Операция", ["Добавить", "Удалить"])

    # 4) Количество
    qty = st.number_input("Количество", min_value=1, step=1)

    # 5) Кнопка проведения операции
    if st.button("Провести операцию"):
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 5.1) Запись в transactions
                cur.execute(
                    "INSERT INTO transactions (item_id, operation, quantity) VALUES (%s, %s, %s)",
                    (item_id, operation.lower(), qty)
                )
                # 5.2) Обновление или вставка в warehouse
                cur.execute(
                    "SELECT quantity FROM warehouse WHERE item_id = %s",
                    (item_id,)
                )
                res = cur.fetchone()
                if res:
                    current_qty = res[0]
                    new_qty = current_qty + qty if operation == "Добавить" else current_qty - qty
                    if new_qty < 0:
                        st.error("Недостаточно товара на складе.")
                        conn.rollback()
                        return
                    cur.execute(
                        "UPDATE warehouse SET quantity = %s, last_updated = NOW() WHERE item_id = %s",
                        (new_qty, item_id)
                    )
                else:
                    if operation == "Удалить":
                        st.error("На складе нет такого товара.")
                        conn.rollback()
                        return
                    cur.execute(
                        "INSERT INTO warehouse (item_id, quantity) VALUES (%s, %s)",
                        (item_id, qty)
                    )
            conn.commit()
        st.success("Операция успешно проведена.")