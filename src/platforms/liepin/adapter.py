import subprocess, sys, json, time
from pathlib import Path
from src.core.database import log

ROOT = Path("/tmp/auto-job-tools/Auto-JobHunter")
BASE = ROOT / "liepin_scraper"
COOKIE = BASE / "liepin_cookies.json"

CLI_ARGS = ["-p", "--page", "--keyword", "--city", "--salary"]

def login():
    log("liepin", "login_start")
    r = subprocess.run(
        [sys.executable, str(BASE / "liepin_cookie_harvester.py")],
        cwd=BASE, timeout=180)
    ok = r.returncode == 0 and COOKIE.exists()
    log("liepin", "login_ok" if ok else "login_fail")
    return ok

def search(keyword, city="深圳", pages=2):
    if not COOKIE.exists():
        print("[!] 猎聘未登录。运行: python src/cli.py liepin login")
        return []
    log("liepin", "search_start", f"{keyword}@{city}")
    for p in range(1, pages + 1):
        try:
            subprocess.run(
                [sys.executable, str(BASE / "liepin_crawler.py"),
                 "-p", str(p), "--keyword", keyword, "--city", city],
                cwd=ROOT, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            print(f"  [!] 猎聘第{p}页超时")
    return _read_db()

def _read_db():
    db = ROOT / "data" / "job_hunter.db"
    if not db.exists():
        return []
    import sqlite3
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM raw_jobs WHERE platform='猎聘' ORDER BY crawl_time DESC LIMIT 50")]
    conn.close()
    log("liepin", "search_done", f"found={len(rows)}")
    return rows
