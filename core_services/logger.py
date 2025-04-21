import datetime
from connect import get_mongo_connection
import streamlit as st

def log_action(action: str, params: dict = None):
    """
    Записывает в MongoDB: timestamp, имя пользователя из st.session_state,
    название действия и любые параметры (dict).
    """
    client = get_mongo_connection()
    db = client["srm_logs"]                     # имя БД — по вашему вкусу
    collection = db["action_logs"]              # имя коллекции
    log = {
        "timestamp": datetime.datetime.utcnow(),
        "username": st.session_state.get("username"),
        "action": action,
        "params": params or {}
    }
    collection.insert_one(log)