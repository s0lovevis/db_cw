from typing import List, Tuple
from connect import get_connection

def get_access_rights_by_role(role_name: str) -> List[Tuple[str, str]]:
    query = """
        SELECT ar.name, ar.description
        FROM access_rights ar
        JOIN roles r ON ar.role_id = r.role_id
        WHERE r.name = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (role_name,))
            return cur.fetchall()