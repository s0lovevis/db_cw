# Файлик с инициализирующей загрузкой БДшки

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

    CREATE TABLE IF NOT EXISTS roles (
        role_id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS access_rights (
        right_id SERIAL PRIMARY KEY,
        role_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        FOREIGN KEY (role_id) REFERENCES roles(role_id)
    );

    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        reg_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        role_id INT NOT NULL,
        FOREIGN KEY (role_id) REFERENCES roles(role_id)
    );

-- Создание таблицы юридических адресов
    CREATE TABLE IF NOT EXISTS legal_addresses (
        address_id SERIAL PRIMARY KEY,
        city VARCHAR(100) NOT NULL,
        street VARCHAR(100) NOT NULL,
        house VARCHAR(10) NOT NULL,
        building VARCHAR(10)
    );

    -- Создание таблицы ЛПР (лиц, принимающих решения)
    CREATE TABLE IF NOT EXISTS decision_makers (
        dm_id SERIAL PRIMARY KEY,
        last_name VARCHAR(50) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        middle_name VARCHAR(50),
        age INT CHECK (age > 0)
    );

    -- Создание таблицы поставщиков
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id SERIAL PRIMARY KEY,
        company_name VARCHAR(100) NOT NULL,
        inn VARCHAR(12) NOT NULL UNIQUE,
        ogrn VARCHAR(13) NOT NULL UNIQUE,
        address_id INT NOT NULL,
        dm_id INT NOT NULL,
        FOREIGN KEY (address_id) REFERENCES legal_addresses(address_id),
        FOREIGN KEY (dm_id) REFERENCES decision_makers(dm_id)
    );

    INSERT INTO roles (name, description)
    SELECT 'admin', 'Администратор CRM-системы'
    WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'admin');

    INSERT INTO roles (name, description)
    SELECT 'manager', 'Менеджер по работе с поставщиками'
    WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'manager');

    INSERT INTO roles (name, description)
    SELECT 'warehouse_worker', 'Сотрудник склада'
    WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'warehouse_worker');

    INSERT INTO users (username, password_hash, role_id)
    SELECT 'admin', crypt('admin', gen_salt('bf')), (SELECT role_id FROM roles WHERE name = 'admin')
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

    INSERT INTO users (username, password_hash, role_id)
    SELECT 'manager', crypt('manager', gen_salt('bf')), (SELECT role_id FROM roles WHERE name = 'manager')
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'manager');

    INSERT INTO users (username, password_hash, role_id)
    SELECT 'worker', crypt('worker', gen_salt('bf')), (SELECT role_id FROM roles WHERE name = 'warehouse_worker')
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'worker');

    
    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'admin'), 
        'add_new_user', 
        'Добавление нового пользователя в систему'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'add_new_user' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'admin')
    );

    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'admin'), 
        'change_password', 
        'Смена пароля'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'change_password' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'admin')
    );

    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'manager'), 
        'change_password', 
        'Смена пароля'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'change_password' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'manager')
    );

    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'warehouse_worker'), 
        'change_password', 
        'Смена пароля'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'change_password' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'warehouse_worker')
    );

    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'admin'), 
        'delete_user', 
        'Удаление пользователя'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'delete_user' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'admin')
    );

    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'admin'), 
        'view_users', 
        'Просмотр списка сотрудников'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'view_users' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'admin')
    );

-- Добавление прав для управления адресами
    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'manager'), 
        'manage_addresses', 
        'Управление адресами поставщиков'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'manage_addresses' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'manager')
    );

    -- Добавление прав для управления ЛПР
    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'manager'), 
        'manage_decision_makers', 
        'Управление базой ЛПРов'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'manage_decision_makers' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'manager')
    );

    -- Добавление прав для управления поставщиками
    INSERT INTO access_rights (role_id, name, description)
    SELECT 
        (SELECT role_id FROM roles WHERE name = 'manager'), 
        'manage_suppliers', 
        'Управление базой поставщиков'
    WHERE NOT EXISTS (
        SELECT 1 FROM access_rights 
        WHERE name = 'manage_suppliers' 
        AND role_id = (SELECT role_id FROM roles WHERE name = 'manager')
    );
    """

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql_script)
        conn.commit()
        
        print("База данных успешно инициализирована!")
        
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()