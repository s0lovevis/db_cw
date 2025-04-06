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

    INSERT INTO roles (name, description)
    SELECT 'admin', 'Администратор CRM-системы'
    WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'admin');

    INSERT INTO roles (name, description)
    SELECT 'manager', 'Менеджер по работе с поставщиками'
    WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'manager');

    INSERT INTO users (username, password_hash, role_id)
    SELECT 'admin', crypt('admin', gen_salt('bf')), (SELECT role_id FROM roles WHERE name = 'admin')
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

    INSERT INTO users (username, password_hash, role_id)
    SELECT 'manager', crypt('manager', gen_salt('bf')), (SELECT role_id FROM roles WHERE name = 'manager')
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'manager');

    
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