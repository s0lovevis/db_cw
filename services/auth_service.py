from typing import Optional, Tuple
import psycopg2
from connect import get_connection

def authenticate_user(username: str, password: str) -> Optional[Tuple[str, str]]:
    query = """
        SELECT u.username, r.name AS role
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.username = %s AND u.password_hash = crypt(%s, u.password_hash)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username, password))
            result = cur.fetchone()
            return result if result else None
