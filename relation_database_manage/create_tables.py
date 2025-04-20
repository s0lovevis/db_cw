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

    CREATE TABLE IF NOT EXISTS catalog (
        item_id SERIAL PRIMARY KEY,
        supplier_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        length NUMERIC,
        width NUMERIC,
        height NUMERIC,
        price NUMERIC,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
    );

    -- Сущность транзакций (операций по складу)
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id   SERIAL    PRIMARY KEY,
        item_id          INT       NOT NULL,
        operation        VARCHAR(10) NOT NULL,      -- 'Добавить' или 'Удалить'
        quantity         NUMERIC    NOT NULL,
        monetary_volume  NUMERIC    NOT NULL,       -- денежный объём операции
        success          BOOLEAN    NOT NULL,       -- флаг успешности
        transaction_time TIMESTAMP  NOT NULL DEFAULT NOW(),
        FOREIGN KEY (item_id) REFERENCES catalog(item_id)
    );

    -- Сущность текущего состояния склада
    CREATE TABLE IF NOT EXISTS warehouse (
        warehouse_id  SERIAL PRIMARY KEY,
        item_id       INT       NOT NULL,
        quantity      NUMERIC    NOT NULL,
        last_updated  TIMESTAMP NOT NULL DEFAULT NOW(),
        FOREIGN KEY (item_id) REFERENCES catalog(item_id)
    );

    -- Создание таблицы типов заданий
    CREATE TABLE IF NOT EXISTS task_types (
        type_id SERIAL PRIMARY KEY,
        name_en VARCHAR(50) NOT NULL UNIQUE,
        name_ru VARCHAR(100) NOT NULL,
        description TEXT
    );
 
    CREATE TABLE IF NOT EXISTS tasks (
        task_id SERIAL PRIMARY KEY,
        type_id INT NOT NULL,
        creator_username VARCHAR(50) NOT NULL,
        assignee_username VARCHAR(50) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP WITH TIME ZONE,
        FOREIGN KEY (type_id) REFERENCES task_types(type_id)
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

def fill_initial_data():
    sql_script = """
    -- Адреса
    INSERT INTO legal_addresses (city, street, house, building) VALUES
    ('Москва', 'Ленинская', '10', '1'),
    ('Санкт-Петербург', 'Невский проспект', '25', NULL),
    ('Казань', 'Баумана', '3', 'А');

    -- ЛПРы
    INSERT INTO decision_makers (last_name, first_name, middle_name, age) VALUES
    ('Иванов', 'Иван', 'Иванович', 45),
    ('Петров', 'Петр', 'Петрович', 38),
    ('Сидоров', 'Сидор', NULL, 50);

    -- Поставщики (привязка к адресам и ЛПРам)
    INSERT INTO suppliers (company_name, inn, ogrn, address_id, dm_id) VALUES
    ('ООО Альфа', '7701234567', '1027700000001', 1, 1),
    ('ООО Бета', '7809876543', '1027800000002', 2, 2),
    ('ООО Гамма', '1654321987', '1021600000003', 3, 3);

    -- Каталог товаров (привязка к поставщикам)
    INSERT INTO catalog (supplier_id, name, description, length, width, height, price) VALUES
    (1, 'Ящик алюминиевый', 'Прочный ящик для хранения', 40, 30, 20, 1500),
    (1, 'Палета деревянная', 'Палета 120x80 стандарт', 120, 80, 15, 800),
    (2, 'Контейнер пластиковый', 'Герметичный пластиковый контейнер', 60, 40, 35, 1200),
    (3, 'Короб архивный', 'Картонная коробка для документов', 35, 25, 10, 300);

    -- Инициализация склада (только те товары, что из каталога)
    INSERT INTO warehouse (item_id, quantity) VALUES
        ((SELECT item_id FROM catalog WHERE name = 'Ящик алюминиевый'), 10),
        ((SELECT item_id FROM catalog WHERE name = 'Палета деревянная'), 5);

    -- Добавление начального типа задания
    INSERT INTO task_types (name_en, name_ru, description)
    VALUES
        ('catalog_task', 'Работа с каталогом', 'adfsdf'),
        ('dm_task', 'Работа с базой ЛПРов', 'adfsdf'),
        ('address_task', 'Работа с адресами поставщиков', 'adfsdf'),
        ('supplier_task', 'Работа с данными поставщиков', 'adfsdf'),
        ('warehouse_task', 'Работа со складским учетом', 'adfsdf'),
        ('buy_task', 'Работа с заказом товара', 'adfsdf')
    ON CONFLICT (name_en) DO NOTHING;
    """

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql_script)
        conn.commit()
        print("Начальные данные успешно добавлены.")
    except Exception as e:
        print(f"Ошибка при добавлении данных: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()
    fill_initial_data()