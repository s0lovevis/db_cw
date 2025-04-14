import streamlit as st
from connect import get_connection
import pandas as pd

def render_manage_suppliers():
    st.title("🏢 Управление базой поставщиков")

    # Функция добавления поставщика
    def add_supplier(company_name, inn, ogrn, address_id, dm_id):
        if not company_name or not inn or not ogrn or not address_id or not dm_id:
            st.warning("Пожалуйста, заполните все обязательные поля.")
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Проверка уникальности ИНН и ОГРН
                cur.execute("SELECT 1 FROM suppliers WHERE inn = %s", (inn,))
                if cur.fetchone():
                    st.error("Поставщик с таким ИНН уже существует.")
                    return
                cur.execute("SELECT 1 FROM suppliers WHERE ogrn = %s", (ogrn,))
                if cur.fetchone():
                    st.error("Поставщик с таким ОГРН уже существует.")
                    return
                # Проверка существования address_id и dm_id
                cur.execute("SELECT 1 FROM legal_addresses WHERE address_id = %s", (address_id,))
                if not cur.fetchone():
                    st.error("Адрес с таким ID не найден.")
                    return
                cur.execute("SELECT 1 FROM decision_makers WHERE dm_id = %s", (dm_id,))
                if not cur.fetchone():
                    st.error("ЛПР с таким ID не найден.")
                    return
                cur.execute(
                    "INSERT INTO suppliers (company_name, inn, ogrn, address_id, dm_id) VALUES (%s, %s, %s, %s, %s)",
                    (company_name, inn, ogrn, address_id, dm_id)
                )
                conn.commit()
                st.success("Поставщик добавлен.")

    # Функция изменения поставщика
    def update_supplier(supplier_id, company_name, inn, ogrn, address_id, dm_id):
        if not company_name or not inn or not ogrn or not address_id or not dm_id:
            st.warning("Пожалуйста, заполните все обязательные поля.")
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Проверка существования поставщика
                cur.execute("SELECT 1 FROM suppliers WHERE supplier_id = %s", (supplier_id,))
                if not cur.fetchone():
                    st.error("Поставщик с таким ID не найден.")
                    return
                # Проверка уникальности ИНН и ОГРН (исключая текущего поставщика)
                cur.execute("SELECT 1 FROM suppliers WHERE inn = %s AND supplier_id != %s", (inn, supplier_id))
                if cur.fetchone():
                    st.error("Поставщик с таким ИНН уже существует.")
                    return
                cur.execute("SELECT 1 FROM suppliers WHERE ogrn = %s AND supplier_id != %s", (ogrn, supplier_id))
                if cur.fetchone():
                    st.error("Поставщик с таким ОГРН уже существует.")
                    return
                # Проверка существования address_id и dm_id
                cur.execute("SELECT 1 FROM legal_addresses WHERE address_id = %s", (address_id,))
                if not cur.fetchone():
                    st.error("Адрес с таким ID не найден.")
                    return
                cur.execute("SELECT 1 FROM decision_makers WHERE dm_id = %s", (dm_id,))
                if not cur.fetchone():
                    st.error("ЛПР с таким ID не найден.")
                    return
                cur.execute(
                    "UPDATE suppliers SET company_name = %s, inn = %s, ogrn = %s, address_id = %s, dm_id = %s WHERE supplier_id = %s",
                    (company_name, inn, ogrn, address_id, dm_id, supplier_id)
                )
                conn.commit()
                st.success("Поставщик обновлен.")

    # Функция удаления поставщика
    def delete_supplier(supplier_id):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM suppliers WHERE supplier_id = %s", (supplier_id,))
                if not cur.fetchone():
                    st.error("Поставщик с таким ID не найден.")
                    return
                cur.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
                conn.commit()
                st.success("Поставщик удален.")

    # Функция выгрузки всех поставщиков
    def view_suppliers():
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
        df = pd.DataFrame(rows, columns=[
            "Название компании", "ИНН",
            "Город", "Улица", "Дом", "Строение",
            "Фамилия ЛПР", "Имя ЛПР", "Отчество ЛПР", "Возраст ЛПР"
        ])
        st.dataframe(df, use_container_width=True)

    # UI для управления поставщиками
    action = st.selectbox("Выберите действие", ["Посмотреть всех поставщиков", "Добавить поставщика", "Изменить поставщика", "Удалить поставщика"])

    if action == "Посмотреть всех поставщиков":
        view_suppliers()

    elif action == "Добавить поставщика":
        company_name = st.text_input("Название компании")
        inn = st.text_input("ИНН")
        ogrn = st.text_input("ОГРН")

        # Загружаем адреса
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT address_id, city, street, house, building FROM legal_addresses")
                addresses = cur.fetchall()
                cur.execute("SELECT dm_id, last_name, first_name, middle_name FROM decision_makers")
                dms = cur.fetchall()

        if not addresses:
            st.info("Сначала добавьте хотя бы один адрес.")
            return
        if not dms:
            st.info("Сначала добавьте хотя бы одного ЛПР.")
            return

        address_map = {f"{a[1]}, {a[2]}, {a[3]}, {a[4]}": a[0] for a in addresses}
        address_choice = st.selectbox("Выберите адрес", list(address_map.keys()))
        address_id = address_map[address_choice]

        dm_map = {f"{d[1]} {d[2]} {d[3]}": d[0] for d in dms}
        dm_choice = st.selectbox("Выберите ЛПР", list(dm_map.keys()))
        dm_id = dm_map[dm_choice]

        if st.button("Добавить"):
            add_supplier(company_name, inn, ogrn, address_id, dm_id)


    elif action == "Изменить поставщика":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT supplier_id, company_name, inn FROM suppliers")
                suppliers = cur.fetchall()
                cur.execute("SELECT address_id, city, street, house, building FROM legal_addresses")
                addresses = cur.fetchall()
                cur.execute("SELECT dm_id, last_name, first_name, middle_name FROM decision_makers")
                dms = cur.fetchall()

        if not suppliers:
            st.info("Нет поставщиков для изменения.")
            return
        if not addresses:
            st.info("Сначала добавьте хотя бы один адрес.")
            return
        if not dms:
            st.info("Сначала добавьте хотя бы одного ЛПР.")
            return

        supplier_map = {f"{s[1]} (ИНН: {s[2]})": s[0] for s in suppliers}
        supplier_choice = st.selectbox("Выберите поставщика", list(supplier_map.keys()))
        supplier_id = supplier_map[supplier_choice]

        company_name = st.text_input("Новое название компании")
        inn = st.text_input("Новый ИНН")
        ogrn = st.text_input("Новый ОГРН")

        address_map = {f"{a[1]}, {a[2]}, {a[3]}, {a[4]}": a[0] for a in addresses}
        address_choice = st.selectbox("Выберите новый адрес", list(address_map.keys()))
        address_id = address_map[address_choice]

        dm_map = {f"{d[1]} {d[2]} {d[3]}": d[0] for d in dms}
        dm_choice = st.selectbox("Выберите нового ЛПР", list(dm_map.keys()))
        dm_id = dm_map[dm_choice]

        if st.button("Изменить"):
            update_supplier(supplier_id, company_name, inn, ogrn, address_id, dm_id)



    elif action == "Удалить поставщика":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT supplier_id, company_name, inn FROM suppliers")
                suppliers = cur.fetchall()

        if not suppliers:
            st.info("Нет поставщиков для удаления.")
            return

        supplier_map = {f"{s[1]} (ИНН: {s[2]})": s[0] for s in suppliers}
        selected = st.selectbox("Выберите поставщика для удаления", list(supplier_map.keys()))
        supplier_id = supplier_map[selected]

        if st.button("Удалить"):
            delete_supplier(supplier_id)