from __future__ import annotations

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from db_config import get_db_connection, execute_query

def init_db() -> None:
    # Schema creation logic is now primarily handled by migrations (db_migrate.py) or external DDL.
    # For compatibility, we can keep ensuring tables exist for SQLite dev environment,
    # but for production PG, we rely on migrations.
    # Here we just pass, or we could run specific checks.
    # Let's keep it simple and assume schema is managed.
    pass

def upsert_user(user_id: str, name: str, role: str) -> None:
    execute_query("""
    INSERT INTO users(user_id, name, role, created_at)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT(user_id) DO UPDATE SET name=excluded.name, role=excluded.role
    """, (user_id, name, role, time.strftime("%Y-%m-%d %H:%M:%S")))

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    rows = execute_query("SELECT * FROM users WHERE user_id=%s", (user_id,), fetch=True)
    return rows[0] if rows else None

def set_workflow(property_id: str, status: str, supplier_id: Optional[str] = None, note: str = "") -> None:
    # Note: SQLite supports ON CONFLICT, Postgres ON CONFLICT requires specific syntax.
    # db_migrate.py handles schema differences but query syntax might need attention.
    # Standard SQL: INSERT ... ON CONFLICT (property_id) DO UPDATE ...
    # This syntax works for both modern SQLite and PostgreSQL.
    
    # However, property_workflow table must have property_id as PK or UNIQUE index.
    
    # We need to handle the COALESCE logic carefully or just pass supplier_id if we want to overwrite.
    # The original query used `COALESCE(excluded.supplier_id, property_workflow.supplier_id)`.
    # `excluded` keyword is valid in PG and SQLite.
    
    execute_query("""
    INSERT INTO property_workflow(property_id, status, supplier_id, updated_at, note)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT(property_id) DO UPDATE SET
        status=excluded.status,
        supplier_id=COALESCE(excluded.supplier_id, property_workflow.supplier_id),
        updated_at=excluded.updated_at,
        note=excluded.note
    """, (property_id, status, supplier_id, time.strftime("%Y-%m-%d %H:%M:%S"), note))

def get_workflow(property_id: str) -> Optional[Dict[str, Any]]:
    rows = execute_query("SELECT * FROM property_workflow WHERE property_id=%s", (property_id,), fetch=True)
    return rows[0] if rows else None

def list_workflows(limit: int = 200) -> List[Dict[str, Any]]:
    return execute_query("""
        SELECT * FROM property_workflow
        ORDER BY updated_at DESC
        LIMIT %s
    """, (limit,), fetch=True)

def audit(user_id: str, role: str, action: str, property_id: str = "", detail: str = "") -> None:
    execute_query("""
    INSERT INTO audit_log(ts, user_id, role, action, property_id, detail)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (time.strftime("%Y-%m-%d %H:%M:%S"), user_id, role, action, property_id, detail))

def list_audit(limit: int = 300) -> List[Dict[str, Any]]:
    return execute_query("""
        SELECT * FROM audit_log
        ORDER BY id DESC
        LIMIT %s
    """, (limit,), fetch=True)

def publish_event(property_id: str, channel: str, result: str, detail: str = "") -> None:
    execute_query("""
    INSERT INTO publish_log(ts, property_id, channel, result, detail)
    VALUES (%s, %s, %s, %s, %s)
    """, (time.strftime("%Y-%m-%d %H:%M:%S"), property_id, channel, result, detail))

def list_publish(limit: int = 200) -> List[Dict[str, Any]]:
    return execute_query("""
        SELECT * FROM publish_log
        ORDER BY id DESC
        LIMIT %s
    """, (limit,), fetch=True)
