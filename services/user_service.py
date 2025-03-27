# services/user_service.py

def authenticate(username, password):
    """
    Заглушка для аутентификации пользователя.
    """
    # Простейшая проверка: если логин и пароль совпадают с предопределенными значениями
    if username == "admin" and password == "admin":
        return {"id": 1, "username": "admin", "role": "admin"}
    elif username == "manager" and password == "manager":
        return {"id": 2, "username": "manager", "role": "manager"}
    elif username == "reader" and password == "reader":
        return {"id": 3, "username": "reader", "role": "reader"}
    return None
