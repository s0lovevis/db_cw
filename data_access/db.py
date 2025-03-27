# data_access/db.py

def get_suppliers():
    """
    Заглушка: возвращает список фейковых поставщиков.
    """
    return [
        {"id": 1, "name": "Поставщик 1", "email": "supplier1@example.com", "phone": "1234567890", "rating": 4.5},
        {"id": 2, "name": "Поставщик 2", "email": "supplier2@example.com", "phone": "0987654321", "rating": 4.2},
    ]

def get_orders():
    """
    Заглушка: возвращает список фейковых заказов.
    """
    return [
        {"id": 1, "supplier_id": 1, "order_date": "2025-01-01", "total_sum": 1000},
        {"id": 2, "supplier_id": 2, "order_date": "2025-01-02", "total_sum": 2000},
    ]

# Здесь можно добавить и другие функции-заглушки для работы с таблицами (contracts, order_items и пр.)
