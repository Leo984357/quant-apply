#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from pathlib import Path
from src.config.loader import load_config
from src.core.database import get_stats, log

def banner():
    print(r"""
    __  ___          _             _   _
   / _|/ _ \        | |           | | | |
  | |_| | | |_  ____| |_ ____   __| | | |  _ __
  |  _| |_| |\ \/ /| __|  _ \ / _  | | | | '_ \
  | | |  _  | >  < | |_| |_) | (_| | | | | |_) |
  |_| |_| |_|/_/\_\ \__| .__/ \__,_| |_| | .__/
                        | |               | |
                        |_|               |_|
    """)

@click.group()
def cli():
    pass

@cli.command()
def setup():
    """One-time setup: check deps, install tools, configure."""
    banner()
    print("[*] Loading config...")
    cfg = load_config()
    profile = cfg["profile"]
    print(f"  Name: {profile['name']} ({profile['name_cn']})")
    print(f"  School: {profile['university']} - {profile['major']}")
    print(f"  Location: {profile['location']}")

    print("\n[*] Checking login status...")
    from src.platforms.boss.adapter import status
    st = status()
    if st and st.get("logged_in"):
        print(f"  ✓ Boss直聘 logged in as {st.get('user_name')}")
    else:
        print(f"  ✗ Not logged in. Run: python src/cli.py boss login")

    print("\n[*] Creating database...")
    from src.core.database import get_conn
    get_conn()
    print("  ✓ data/applications.db")

    print("\n[✓] Ready. Next steps:")
    print("  python src/cli.py boss run --city 深圳 --dry-run")

@cli.group()
def boss():
    """Boss直聘 operations."""
    pass

@boss.command()
def login():
    """Login to Boss直聘."""
    from src.platforms.boss.adapter import login as boss_login
    if boss_login():
        print("[✓] Boss login successful")
    else:
        print("[✗] Boss login failed")
        sys.exit(1)

@boss.command()
@click.option("--city", default="深圳", help="City to search")
@click.option("--limit", default=50, help="Max jobs to process")
@click.option("--dry-run", is_flag=True, help="Search only, don't apply")
@click.option("--target-only", is_flag=True, help="Only match target companies")
def run(city, limit, dry_run, target_only):
    """Search and apply to jobs on Boss直聘."""
    from src.platforms.boss.adapter import search, greet_batch
    from src.core.matcher import score_job
    from src.core.database import log_application, update_status

    cfg = load_config()
    boss_cfg = cfg["boss"]
    search_cfg = cfg["search"]
    target_set = set(c.lower() for c in search_cfg["target_companies"])

    print(f"[*] Searching in {city}...")
    jobs = search(search_cfg["titles"], city, limit)
    print(f"  Found {len(jobs)} jobs")

    matched = []
    for job in jobs:
        title = job.get("title", "")
        company = job.get("company", "")

        if target_only and company.lower() not in target_set:
            for t in target_set:
                if t in company.lower():
                    break
            else:
                continue

        score = score_job(title, company, job, cfg)
        if score >= 50:
            matched.append((job.get("job_id", ""), title, company, score))

    print(f"\n  Matched: {len(matched)} jobs")
    for jid, title, company, score in matched:
        print(f"    [{score:2d}] {company} - {title}")

    for jid, title, company, score in matched:
        log_application("boss", company, title, f"https://zhipin.com/job/{jid}", score)

    if dry_run or not matched:
        print("\n[✓] Dry run complete")
        return

    print(f"\n[*] Greeting up to {min(len(matched), 10)} jobs...")
    # Use batch-greet via the CLI's own search + greet flow
    for query in search_cfg["titles"][:3]:
        result = greet_batch(
            query, city=city,
            message=boss_cfg.get("greeting", ""),
            count=min(len(matched), 10),
            dry_run=False,
        )
        if result:
            for c in result.get("candidates", []):
                jid = c.get("job_id") or c.get("security_id", "")
                update_status(f"https://zhipin.com/job/{jid}", "applied")
                print(f"  ✓ {c.get('company')} - {c.get('title')}")
            break

@cli.command()
def stats():
    """Show application statistics."""
    s = get_stats()
    total = sum(s.values())
    print(f"\n📊 Total applications tracked: {total}")
    for status, count in sorted(s.items()):
        print(f"  {status}: {count}")
    log("cli", "stats_viewed")

if __name__ == "__main__":
    cli()
