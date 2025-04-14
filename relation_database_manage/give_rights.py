import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def initialize_database():
    sql_script = """
    CREATE EXTENSION IF NOT EXISTS pgcrypto;

    -- Роли
    INSERT INTO roles (name, description) VALUES 
        ('admin', 'Администратор CRM-системы'),
        ('manager', 'Менеджер по работе с поставщиками'),
        ('warehouse_worker', 'Сотрудник склада');

    -- Пользователи
    INSERT INTO users (username, password_hash, role_id) VALUES 
        ('admin', crypt('admin', gen_salt('bf')), (SELECT role_id FROM roles WHERE name = 'admin')),
        ('manager', crypt('manager', gen_salt('bf')), (SELECT role_id FROM roles WHERE name = 'manager')),
        ('worker', crypt('worker', gen_salt('bf')), (SELECT role_id FROM roles WHERE name = 'warehouse_worker'));

    -- Права доступа
    INSERT INTO access_rights (role_id, name, description) VALUES 
        ((SELECT role_id FROM roles WHERE name = 'admin'), 'add_new_user', 'Добавление нового пользователя в систему'),
        ((SELECT role_id FROM roles WHERE name = 'admin'), 'delete_user', 'Удаление пользователя'),
        ((SELECT role_id FROM roles WHERE name = 'admin'), 'view_users', 'Просмотр списка сотрудников'),

        ((SELECT role_id FROM roles WHERE name = 'admin'), 'change_password', 'Смена пароля'),
        ((SELECT role_id FROM roles WHERE name = 'manager'), 'change_password', 'Смена пароля'),
        ((SELECT role_id FROM roles WHERE name = 'warehouse_worker'), 'change_password', 'Смена пароля'),

        ((SELECT role_id FROM roles WHERE name = 'manager'), 'manage_addresses', 'Управление адресами поставщиков'),
        ((SELECT role_id FROM roles WHERE name = 'manager'), 'manage_decision_makers', 'Управление базой ЛПРов'),
        ((SELECT role_id FROM roles WHERE name = 'manager'), 'manage_suppliers', 'Управление базой поставщиков');
    """

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_script)
        conn.commit()
        print("3 первичных юзера созданы, права выданы!")
    except Exception as e:
        print(f"Ошибка: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()
