import json, sqlite3, time
from pathlib import Path

DB_PATH = Path(__file__).parent / "calllens.db"

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS calls(
          id TEXT PRIMARY KEY, user_id TEXT, filename TEXT, transcript TEXT,
          result TEXT, mode TEXT, stt_seconds REAL, total_seconds REAL, created_at REAL);
        CREATE TABLE IF NOT EXISTS events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, call_id TEXT,
          name TEXT, created_at REAL);
        CREATE TABLE IF NOT EXISTS feedback(
          call_id TEXT PRIMARY KEY, rating INTEGER, confirmed TEXT, comment TEXT, created_at REAL);
        """)

def save_call(row: dict):
    with _conn() as c:
        c.execute("INSERT INTO calls VALUES(:id,:user_id,:filename,:transcript,:result,:mode,:stt_seconds,:total_seconds,:created_at)",
                  {**row, "result": json.dumps(row["result"]), "created_at": time.time()})

def get_call(call_id: str):
    with _conn() as c:
        r = c.execute("SELECT * FROM calls WHERE id=?", (call_id,)).fetchone()
    if not r:
        return None
    d = dict(r); d["result"] = json.loads(d["result"]); return d

def log_event(user_id: str, call_id: str, name: str):
    with _conn() as c:
        c.execute("INSERT INTO events(user_id,call_id,name,created_at) VALUES(?,?,?,?)",
                  (user_id, call_id, name, time.time()))

def save_feedback(call_id: str, rating: int, confirmed: list, comment: str):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO feedback VALUES(?,?,?,?,?)",
                  (call_id, rating, json.dumps(confirmed), comment, time.time()))

def all_rows(table: str):
    with _conn() as c:
        return [dict(r) for r in c.execute(f"SELECT * FROM {table}").fetchall()]
