import streamlit as st
from connect import get_connection
import pandas as pd

def render_manage_catalog():
    st.title("📦 Управление каталогом товаров")

    # Добавление товара
    def add_item(supplier_id, name, description, length, width, height, price):
        if not name or not price:
            st.warning("Пожалуйста, заполните обязательные поля: название и цена.")
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO catalog (supplier_id, name, description, length, width, height, price) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (supplier_id, name, description, length, width, height, price)
                )
                conn.commit()
                st.success("Товар добавлен в каталог.")

    # Обновление товара
    def update_item(item_id, name, description, length, width, height, price):
        if not name or not price:
            st.warning("Пожалуйста, заполните обязательные поля: название и цена.")
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM catalog WHERE item_id = %s", (item_id,))
                if not cur.fetchone():
                    st.error("Товар с таким ID не найден.")
                    return
                cur.execute("""
                    UPDATE catalog SET name = %s, description = %s, length = %s, width = %s, height = %s, price = %s
                    WHERE item_id = %s
                """, (name, description, length, width, height, price, item_id))
                conn.commit()
                st.success("Товар обновлён.")

    # Удаление товара
    def delete_item(item_id):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM catalog WHERE item_id = %s", (item_id,))
                if not cur.fetchone():
                    st.error("Товар с таким ID не найден.")
                    return
                cur.execute("DELETE FROM catalog WHERE item_id = %s", (item_id,))
                conn.commit()
                st.success("Товар удалён.")

    # Просмотр всех товаров
    def view_items():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.name, s.company_name, s.inn, c.description, c.length, c.width, c.height, c.price
                    FROM catalog c
                    JOIN suppliers s ON c.supplier_id = s.supplier_id
                """)
                rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=[
            "Наименование", "Поставщик", "ИНН", "Описание",
            "Длина", "Ширина", "Высота", "Цена"
        ])
        st.dataframe(df, use_container_width=True)

    action = st.selectbox("Выберите действие", ["Посмотреть каталог", "Добавить товар", "Изменить товар", "Удалить товар"])

    if action == "Посмотреть каталог":
        view_items()

    elif action == "Добавить товар":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT supplier_id, company_name, inn FROM suppliers")
                suppliers = cur.fetchall()
        if not suppliers:
            st.info("Нет доступных поставщиков. Сначала добавьте их.")
            return

        supplier_map = {f"{s[1]} (ИНН - {s[2]})": s[0] for s in suppliers}
        supplier_choice = st.selectbox("Выберите поставщика", list(supplier_map.keys()))
        supplier_id = supplier_map[supplier_choice]

        name = st.text_input("Название товара")
        description = st.text_area("Описание")
        length = st.number_input("Длина (см)", min_value=0.0)
        width = st.number_input("Ширина (см)", min_value=0.0)
        height = st.number_input("Высота (см)", min_value=0.0)
        price = st.number_input("Цена (руб)", min_value=0.0)

        if st.button("Добавить"):
            add_item(supplier_id, name, description, length, width, height, price)

    elif action == "Изменить товар":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.item_id, c.name, s.company_name
                    FROM catalog c
                    JOIN suppliers s ON c.supplier_id = s.supplier_id
                """)
                items = cur.fetchall()

        if not items:
            st.info("Нет товаров для изменения.")
            return

        item_map = {f"{i[1]} от {i[2]}": i[0] for i in items}
        selected = st.selectbox("Выберите товар", list(item_map.keys()))
        item_id = item_map[selected]

        name = st.text_input("Новое название товара")
        description = st.text_area("Новое описание")
        length = st.number_input("Новая длина (см)", min_value=0.0)
        width = st.number_input("Новая ширина (см)", min_value=0.0)
        height = st.number_input("Новая высота (см)", min_value=0.0)
        price = st.number_input("Новая цена (руб)", min_value=0.0)

        if st.button("Изменить"):
            update_item(item_id, name, description, length, width, height, price)

    elif action == "Удалить товар":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.item_id, c.name, s.company_name
                    FROM catalog c
                    JOIN suppliers s ON c.supplier_id = s.supplier_id
                """)
                items = cur.fetchall()

        if not items:
            st.info("Нет товаров для удаления.")
            return

        item_map = {f"{i[1]} от {i[2]}": i[0] for i in items}
        selected = st.selectbox("Выберите товар для удаления", list(item_map.keys()))
        item_id = item_map[selected]

        if st.button("Удалить"):
            delete_item(item_id)
