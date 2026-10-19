from src.schema import connect_readonly

SQL = """
SELECT Country FROM Customer GROUP BY Country ORDER BY COUNT(CustomerId) DESC LIMIT 1;
"""

conn = connect_readonly()
cur = conn.execute(SQL)
print([d[0] for d in cur.description])  # column names
for row in cur.fetchmany(20):           # first 20 rows
    print(row)
conn.close()