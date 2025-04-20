import streamlit as st
from connect import get_connection

def render_manage_warehouse():
    st.title("🏭 Управление складом")

    # 1) Получаем список товаров из каталога
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.item_id, c.name, s.company_name
                FROM catalog c
                JOIN suppliers s ON c.supplier_id = s.supplier_id
                """
            )
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

    # При удалении — запрашиваем цену продажи
    sale_price = None
    if operation == "Удалить":
        sale_price = st.number_input(
            "Цена продажи", min_value=0.0, step=0.01, format="%.2f"
        )

    # 4) Количество
    qty = st.number_input("Количество", min_value=1, step=1)

    # 5) Кнопка проведения операции
    if st.button("Провести операцию"):
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 5.1) получаем цену из каталога
                cur.execute(
                    "SELECT price FROM catalog WHERE item_id = %s",
                    (item_id,)
                )
                price_catalog = cur.fetchone()[0]

                # 5.2) вычисляем денежный объём
                if operation == "Добавить":
                    monetary_volume = price_catalog * qty
                else:
                    monetary_volume = (sale_price or 0) * qty

                # 5.3) по умолчанию считаем успешным
                success = True

                # 5.4) попытка изменения склада
                cur.execute(
                    "SELECT quantity FROM warehouse WHERE item_id = %s",
                    (item_id,)
                )
                row = cur.fetchone()
                if row:
                    current_qty = row[0]
                    if operation == "Добавить":
                        new_qty = current_qty + qty
                        cur.execute(
                            "UPDATE warehouse SET quantity = %s, last_updated = NOW() WHERE item_id = %s",
                            (new_qty, item_id)
                        )
                    else:  # Удаление
                        if current_qty < qty:
                            success = False
                            st.error("Недостаточно товара на складе.")
                        else:
                            new_qty = current_qty - qty
                            cur.execute(
                                "UPDATE warehouse SET quantity = %s, last_updated = NOW() WHERE item_id = %s",
                                (new_qty, item_id)
                            )
                else:
                    if operation == "Добавить":
                        cur.execute(
                            "INSERT INTO warehouse (item_id, quantity) VALUES (%s, %s)",
                            (item_id, qty)
                        )
                    else:
                        success = False
                        st.error("На складе нет такого товара.")

                # 5.5) сохраняем транзакцию в любом случае
                cur.execute(
                    """
                    INSERT INTO transactions
                        (item_id, operation, quantity, monetary_volume, success)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (item_id, operation.lower(), qty, monetary_volume, success)
                )
            conn.commit()
        # 6) итоговый feedback
        if success:
            st.success("Операция успешно проведена.")
