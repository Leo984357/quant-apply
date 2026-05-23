import json, subprocess, os

def score_job(title, company, description, config):
    """Score a job listing against profile (0-100)."""
    search = config["search"]
    score = 50

    title_lower = (title + " " + company).lower()

    for kw in search.get("must_keywords", []):
        if kw.lower() in title_lower:
            score += 10

    for kw in search.get("blocklist_keywords", []):
        if kw.lower() in title_lower:
            score -= 30

    for tc in search.get("target_companies", []):
        if tc.lower() in company.lower():
            score += 20

    return max(0, min(100, score))
