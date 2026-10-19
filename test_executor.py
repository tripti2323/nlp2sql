from src.executor import run_query

tests = {
    "valid": "SELECT Country, COUNT(*) FROM Customer GROUP BY Country ORDER BY 2 DESC LIMIT 3",
    "fenced": "```sql\nSELECT COUNT(*) FROM Track;\n```",
    "delete": "DELETE FROM Customer",
    "drop": "DROP TABLE Customer",
    "two statements": "SELECT 1; SELECT 2",
    "bad column": "SELECT NoSuchColumn FROM Customer",
    "too slow": "SELECT COUNT(*) FROM Track a, Track b, Track c, Track d",
    "many rows": "SELECT * FROM Track",
}

for name, sql in tests.items():
    r = run_query(sql)
    print(f"--- {name}")
    print("ok:", r["ok"], "| rows:", len(r["rows"]), "| truncated:", r["truncated"])
    print("error:", r["error"])