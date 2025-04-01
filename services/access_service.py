from typing import List, Tuple
from connect import get_connection

def get_access_rights_by_role(role_name: str) -> List[Tuple[str, str]]:
    query = """
        SELECT a.name, a.description
        FROM access_rights a
        JOIN roles r ON a.role_id = r.id
        WHERE r.name = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (role_name,))
            return cur.fetchall()