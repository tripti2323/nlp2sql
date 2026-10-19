import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chinook.db"


def connect_readonly(db_path=DB_PATH):
    """Open the database read-only so nothing can change it."""
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _short(value, limit=40):
    """Shorten long values so sample rows don't flood the prompt."""
    if isinstance(value, bytes):
        return "<binary>"
    text = str(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def get_schema_text(db_path=DB_PATH, sample_rows=3):
    """Return the schema (tables, columns, keys) plus sample rows as prompt-ready text."""
    conn = connect_readonly(db_path)
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]

        parts = []
        for table in tables:
            # Columns: (cid, name, type, notnull, default, pk)
            columns = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
            lines = []
            for _, name, col_type, _, _, pk in columns:
                key = " PRIMARY KEY" if pk else ""
                lines.append(f"  {name} {col_type}{key}")

            # Foreign keys: (id, seq, ref_table, from_col, to_col, ...)
            for fk in conn.execute(f'PRAGMA foreign_key_list("{table}")').fetchall():
                ref_col = fk[4] or ""
                lines.append(f"  FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]}({ref_col})")

            block = f"TABLE {table} (\n" + ",\n".join(lines) + "\n)"

            # Sample rows
            col_names = [c[1] for c in columns]
            rows = conn.execute(
                f'SELECT * FROM "{table}" LIMIT {int(sample_rows)}'
            ).fetchall()
            if rows:
                block += f"\n-- sample rows ({', '.join(col_names)}):"
                for row in rows:
                    block += "\n--   " + " | ".join(_short(v) for v in row)

            parts.append(block)

        return "\n\n".join(parts)
    finally:
        conn.close()


if __name__ == "__main__":
    print(get_schema_text())