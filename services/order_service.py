# services/order_service.py
from data_access.db import get_orders
from data_access.redis_client import get_order_status, set_order_status

def list_orders():
    """
    Возвращает список заказов с информацией о статусе.
    """
    orders = get_orders()
    for order in orders:
        order['status'] = get_order_status(order['id'])
    return orders

def update_order_status(order_id, status):
    """
    Обновляет статус заказа.
    """
    set_order_status(order_id, status)
    return True
