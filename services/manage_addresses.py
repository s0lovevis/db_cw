import streamlit as st
from connect import get_connection
import pandas as pd

def render_manage_addresses():
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
    def delete_address(address_id):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM legal_addresses WHERE address_id = %s", (address_id,))
                if not cur.fetchone():
                    st.error("Адрес с таким ID не найден.")
                    return
                cur.execute("DELETE FROM legal_addresses WHERE address_id = %s", (address_id,))
                conn.commit()
                st.success("Адрес удален.")

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
        view_addresses()

    elif action == "Добавить адрес":
        city = st.text_input("Город")
        street = st.text_input("Улица")
        house = st.text_input("Дом")
        building = st.text_input("Строение")
        if st.button("Добавить"):
            add_address(city, street, house, building)

    elif action == "Изменить адрес":
        address_id = st.number_input("ID адреса", min_value=1)
        city = st.text_input("Новый город")
        street = st.text_input("Новая улица")
        house = st.text_input("Новый дом")
        building = st.text_input("Новое строение")
        if st.button("Изменить"):
            update_address(address_id, city, street, house, building)

    elif action == "Удалить адрес":
        address_id = st.number_input("ID адреса", min_value=1)
        if st.button("Удалить"):
            delete_address(address_id)