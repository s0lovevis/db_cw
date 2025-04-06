from typing import Optional, Tuple
from connect import get_connection

def authenticate_user(username: str, password: str) -> Optional[Tuple[str, str]]:
    query = """
        SELECT u.username, r.name, r.description AS role_name
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.username = %s AND u.password_hash = crypt(%s, u.password_hash)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username, password))
            result = cur.fetchone()
            return result if result else None
