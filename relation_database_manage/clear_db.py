# Файлик с ПОЛНЫМ ДРОПОМ всей бдшки

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

def drop_all_relational_db():

    sql_script = """
        drop table if exists users;
        drop table if exists access_rights;
        drop table if exists roles;
        drop table if exists suppliers;
        drop table if exists decision_makers;
        drop table if exists legal_addresses;
    """

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql_script)
        conn.commit()
        
        print("Успех!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    drop_all_relational_db()