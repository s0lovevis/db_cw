# ui/app.py
import streamlit as st
from services.supplier_service import list_suppliers
from services.order_service import list_orders, update_order_status
from services.contract_service import list_contracts
from services.user_service import authenticate

def main():
    
    # Форма авторизации
    if "user" not in st.session_state:
        st.title("CRM для управления отношениями с поставщиками")
        st.subheader("Вход в систему")
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            user = authenticate(username, password)
            if user:
                st.session_state["user"] = user
                st.success("Успешная авторизация!")
            else:
                st.error("Неверные учетные данные")
    
    if "user" in st.session_state:
        user = st.session_state["user"]
        st.sidebar.write("Пользователь: {}".format(user["username"]))
        st.sidebar.write("Роль: {}".format(user["role"]))
        
        # Навигация по страницам
        st.sidebar.title("Меню")
        page = st.sidebar.radio("Навигация", ["Главная", "Поставщики", "Заказы", "Контракты"])
        
        if page == "Главная":
            st.write("Добро пожаловать в систему!")
        
        elif page == "Поставщики":
            st.header("Поставщики")
            suppliers = list_suppliers()
            for supplier in suppliers:
                st.write("ID: {id}, Название: {name}, Email: {email}, Телефон: {phone}, Рейтинг: {rating}".format(**supplier))
        
        elif page == "Заказы":
            st.header("Заказы")
            orders = list_orders()
            for order in orders:
                st.write("ID: {id}, Поставщик: {supplier_id}, Дата заказа: {order_date}, Сумма: {total_sum}, Статус: {status}".format(**order))
            
            # Пример обновления статуса заказа
            order_id = st.number_input("Введите ID заказа для обновления статуса", value=1, step=1)
            new_status = st.text_input("Новый статус")
            if st.button("Обновить статус"):
                update_order_status(order_id, new_status)
                st.success("Статус обновлен")
        
        elif page == "Контракты":
            st.header("Контракты")
            contracts = list_contracts()
            for contract in contracts:
                st.write("ID: {id}, Поставщик: {supplier_id}, Дата начала: {start_date}, Дата окончания: {end_date}, Статус: {status}".format(**contract))

if __name__ == "__main__":
    main()
