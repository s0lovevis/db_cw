import streamlit as st
import psycopg2
from connect import get_connection
from core_services.logger import log_action
import pandas as pd

def render_manage_addresses():
    log_action("open_manage_addresses_page")
    st.title("🏠 Управление адресами поставщиков")

    # Функция добавления адреса
    def add_address(city, street, house, building):
        if not city or not street or not house:
            st.warning("Пожалуйста, заполните все обязательные поля (город, улица, дом).")
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO legal_addresses (city, street, house, building) VALUES (%s, %s, %s, %s)",
                    (city, street, house, building)
                )
                conn.commit()
                st.success("Адрес добавлен.")

    # Функция изменения адреса
    def update_address(address_id, city, street, house, building):
        if not city or not street or not house:
            st.warning("Пожалуйста, заполните все обязательные поля (город, улица, дом).")
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM legal_addresses WHERE address_id = %s", (address_id,))
                if not cur.fetchone():
                    st.error("Адрес с таким ID не найден.")
                    return
                cur.execute(
                    "UPDATE legal_addresses SET city = %s, street = %s, house = %s, building = %s WHERE address_id = %s",
                    (city, street, house, building, address_id)
                )
                conn.commit()
                st.success("Адрес обновлен.")

    # Функция удаления адреса

    def delete_address(address_id: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM legal_addresses WHERE address_id = %s", (address_id,))
                if not cur.fetchone():
                    st.error("Адрес с таким ID не найден.")
                    return
                try:
                    cur.execute("DELETE FROM legal_addresses WHERE address_id = %s", (address_id,))
                    conn.commit()
                    st.success("Адрес удален.")
                except psycopg2.errors.ForeignKeyViolation:
                    conn.rollback()
                    st.error("Невозможно удалить адрес, закрепленный за поставщиком. "
                            "Рекомендуем просто поменять существующий адрес поставщика вместо его пересоздания.")


    # Функция выгрузки всех адресов
    def view_addresses():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT address_id, city, street, house, building FROM legal_addresses")
                rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=["ID адреса", "Город", "Улица", "Дом", "Строение"])
        st.dataframe(df, use_container_width=True)

    # UI для управления адресами
    action = st.selectbox("Выберите действие", ["Посмотреть все адреса", "Добавить адрес", "Изменить адрес", "Удалить адрес"])

    if action == "Посмотреть все адреса":
        log_action("view_addresses")
        view_addresses()

    elif action == "Добавить адрес":
        city = st.text_input("Город")
        street = st.text_input("Улица")
        house = st.text_input("Дом")
        building = st.text_input("Строение")
        if st.button("Добавить"):
            log_action("add_address", {
                "city": city, "street": street,
                "house": house, "building": building
            })
            add_address(city, street, house, building)

    elif action == "Изменить адрес":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT address_id, city, street, house, building FROM legal_addresses")
                addresses = cur.fetchall()

        if not addresses:
            st.info("Нет доступных адресов для изменения.")
            return

        address_map = {f"{a[1]}, {a[2]}, {a[3]}, {a[4]}": a[0] for a in addresses}
        selected = st.selectbox("Выберите адрес", list(address_map.keys()))
        address_id = address_map[selected]

        city = st.text_input("Новый город")
        street = st.text_input("Новая улица")
        house = st.text_input("Новый дом")
        building = st.text_input("Новое строение")
        if st.button("Изменить"):
            update_address(address_id, city, street, house, building)


    elif action == "Удалить адрес":
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT address_id, city, street, house, building FROM legal_addresses")
                addresses = cur.fetchall()

        if not addresses:
            st.info("Нет доступных адресов для удаления.")
            return

        address_map = {f"{a[1]}, {a[2]}, {a[3]}, {a[4]}": a[0] for a in addresses}
        selected = st.selectbox("Выберите адрес для удаления", list(address_map.keys()))
        address_id = address_map[selected]

        if st.button("Удалить"):
            delete_address(address_id)
