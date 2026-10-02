from app.db import connect

# 原案：a_* 四元组 + a_member/b_member 成员快照
# 反案：ca_*/cb_* 四元组 + ca_member/cb_member 成员快照 + proposed_by 提交方
# selected：确认时显式选择的案子（original/counter）
_SWAP_COLUMNS = [
    ("a_member", "INT"), ("b_member", "INT"),
    ("ca_day", "INT"), ("ca_task", "INT"), ("cb_day", "INT"), ("cb_task", "INT"),
    ("ca_member", "INT"), ("cb_member", "INT"), ("proposed_by", "INT"),
    ("selected", "TEXT"),
]

def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS members(id INTEGER PRIMARY KEY, name TEXT, active INT, data_quality TEXT);
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, title TEXT, weight INT, data_quality TEXT);
    CREATE TABLE IF NOT EXISTS weeks(id INTEGER PRIMARY KEY, label TEXT, status TEXT);
    CREATE TABLE IF NOT EXISTS assignments(id INTEGER PRIMARY KEY AUTOINCREMENT, week_id INT, day INT, task_id INT, member_id INT);
    CREATE TABLE IF NOT EXISTS swap_requests(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      week_id INT,
      a_day INT, a_task INT, b_day INT, b_task INT,
      a_member INT, b_member INT,
      ca_day INT, ca_task INT, cb_day INT, cb_task INT,
      ca_member INT, cb_member INT, proposed_by INT,
      selected TEXT,
      status TEXT, note TEXT
    );
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
    """)
    # 旧库增量迁移：缺列则补，已有 pending 数据不丢
    existing = {r["name"] for r in c.execute("PRAGMA table_info(swap_requests)")}
    for name, decl in _SWAP_COLUMNS:
        if name not in existing:
            c.execute(f"ALTER TABLE swap_requests ADD COLUMN {name} {decl}")
    if c.execute("SELECT COUNT(*) c FROM members").fetchone()["c"] == 0:
        c.executemany("INSERT INTO members(name,active,data_quality) VALUES (?,?,?)", [
            ("阿明", 1, "clean"), ("小雨", 1, "clean"), ("爷爷", 1, "clean"),
            ("幽灵成员", 0, "dirty"),
        ])
        c.executemany("INSERT INTO tasks(title,weight,data_quality) VALUES (?,?,?)", [
            ("洗碗", 1, "clean"), ("倒垃圾", 1, "clean"), ("扫地", 2, "clean"),
            ("负权重任务", -1, "dirty"),
        ])
        c.execute("INSERT INTO weeks(label,status) VALUES ('第12周','draft')")
        c.execute("INSERT INTO settings(key,value) VALUES ('household','绿纸之家')")
        c.commit()
    c.close()
