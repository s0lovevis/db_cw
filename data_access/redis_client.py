# data_access/redis_client.py

def get_order_status(order_id):
    """
    Заглушка: возвращает фейковый статус заказа.
    """
    # В реальной реализации здесь будет обращение к Redis
    return "Статус для заказа {}".format(order_id)

def set_order_status(order_id, status):
    """
    Заглушка: устанавливает фейковый статус заказа.
    """
    # Здесь будет логика сохранения статуса в Redis
    print("Установлен статус '{}' для заказа {}".format(status, order_id))
