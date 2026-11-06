import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "f1_manager.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]

print(f"Base de dados: {DB_PATH}")
print(f"Total de tabelas: {len(tables)}\n")

for t in tables:
    c.execute(f"SELECT COUNT(*) FROM {t}")
    count = c.fetchone()[0]
    c.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in c.fetchall()]
    print(f"=== {t} ({count} registos) ===")
    print(f"  Colunas: {', '.join(cols)}\n")

conn.close()
