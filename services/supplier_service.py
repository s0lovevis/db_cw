# services/supplier_service.py
from data_access.db import get_suppliers

def list_suppliers():
    """
    Возвращает список поставщиков с возможной дополнительной обработкой.
    """
    suppliers = get_suppliers()
    # Дополнительная логика (например, сортировка или фильтрация) может быть добавлена здесь
    return suppliers
