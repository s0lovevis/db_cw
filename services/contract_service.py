# services/contract_service.py

def list_contracts():
    """
    Заглушка: возвращает список фейковых контрактов.
    """
    return [
        {"id": 1, "supplier_id": 1, "start_date": "2025-01-01", "end_date": "2025-12-31", "status": "Активен"},
        {"id": 2, "supplier_id": 2, "start_date": "2025-02-01", "end_date": "2025-11-30", "status": "Завершен"},
    ]
