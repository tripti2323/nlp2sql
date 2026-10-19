import re
import sqlite3
import time

import sqlparse

from src.schema import connect_readonly

MAX_ROWS = 100
TIMEOUT_SECONDS = 5


def clean_sql(text):
    """Strip markdown fences, whitespace and a trailing semicolon."""
    text = text.strip()
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1)
    return text.strip().rstrip(";").strip()


def validate_select(sql):
    """Return an error message if the SQL is not a single SELECT, else None."""
    if not sql:
        return "Empty query."
    statements = [s for s in sqlparse.split(sql) if s.strip()]
    if len(statements) != 1:
        return "Only a single SQL statement is allowed."
    statement_type = sqlparse.parse(statements[0])[0].get_type()
    if statement_type != "SELECT":
        return f"Only SELECT queries are allowed (got {statement_type})."
    return None


def run_query(raw_sql, max_rows=MAX_ROWS, timeout=TIMEOUT_SECONDS):
    """Clean, validate and safely run a query. Always returns a dict, never raises."""
    sql = clean_sql(raw_sql)
    result = {
        "ok": False,
        "sql": sql,
        "columns": [],
        "rows": [],
        "truncated": False,
        "error": None,
    }

    problem = validate_select(sql)
    if problem:
        result["error"] = problem
        return result

    conn = connect_readonly()  # read-only: writes are impossible
    start = time.time()
    # Called every 10,000 steps; returning 1 aborts the query.
    conn.set_progress_handler(
        lambda: 1 if time.time() - start > timeout else 0, 10000
    )
    try:
        cursor = conn.execute(sql)
        result["columns"] = [d[0] for d in cursor.description] if cursor.description else []
        rows = cursor.fetchmany(max_rows + 1)
        if len(rows) > max_rows:
            result["truncated"] = True
            rows = rows[:max_rows]
        result["rows"] = rows
        result["ok"] = True
    except sqlite3.OperationalError as e:
        message = str(e)
        if "interrupted" in message:
            message = f"Query took longer than {timeout} seconds and was stopped."
        result["error"] = message
    except sqlite3.Error as e:
        result["error"] = str(e)
    finally:
        conn.close()
    return result