import subprocess, json, sys
from src.core.database import log_application, log
from src.config.loader import load_config

BOSSCLI = "boss"

def _boss_json(*args, timeout=120):
    r = subprocess.run(
        [BOSSCLI] + list(args),
        capture_output=True, text=True, timeout=timeout
    )
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None

def login():
    log("boss", "login_start")
    r = subprocess.run([BOSSCLI, "login"], capture_output=True, text=True)
    print(r.stdout, file=sys.stderr)
    if r.returncode == 0:
        log("boss", "login_ok")
        return True
    log("boss", "login_fail", r.stderr)
    return False

def search(queries, city="深圳", limit=50):
    results = []
    seen = set()
    for q in queries:
        data = _boss_json("search", q, "--city", city, "--page", "1")
        if data and data.get("ok"):
            items = data.get("data", [])
            for item in items:
                jid = item.get("job_id") or item.get("security_id", "")
                if jid and jid not in seen:
                    seen.add(jid)
                    results.append({
                        "job_id": jid,
                        "title": item.get("title", ""),
                        "company": item.get("company", ""),
                        "salary": item.get("salary", ""),
                        "city": item.get("city", city),
                        "experience": item.get("experience", ""),
                        "education": item.get("education", ""),
                        "skills": item.get("skills", []),
                        "welfare": item.get("welfare", []),
                        "industry": item.get("industry", ""),
                        "scale": item.get("scale", ""),
                        "boss_name": item.get("boss_name", ""),
                        "boss_title": item.get("boss_title", ""),
                        "boss_active": item.get("boss_active", ""),
                        "greeted": item.get("greeted", False),
                    })
            if len(results) >= limit:
                break
    return results[:limit]

def greet_single(security_id, job_id, message=""):
    cmd = [BOSSCLI, "greet", security_id, job_id]
    if message:
        cmd += ["--message", message]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode == 0:
        data = json.loads(r.stdout)
        return data.get("ok", False)
    return False

def greet_batch(query, city="深圳", message="", count=5, dry_run=False):
    cmd = [BOSSCLI, "batch-greet", query, "--city", city, "--count", str(count)]
    if message:
        cmd += ["--message", message]
    if dry_run:
        cmd += ["--dry-run"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        log("boss", "batch_greet_fail", r.stderr)
        return False
    try:
        result = json.loads(r.stdout)
        if result.get("ok"):
            greeted = result.get("data", {}).get("candidates", [])
            log("boss", "batch_greet", f"count={len(greeted)} dry_run={dry_run}")
            return result["data"]
        return False
    except json.JSONDecodeError:
        return False

def status():
    data = _boss_json("status")
    if data and data.get("ok"):
        return data.get("data", {})
    return None
