from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

def load_config():
    return {
        "profile": load_yaml(ROOT / "config" / "profile.yaml"),
        "search": load_yaml(ROOT / "config" / "search.yaml"),
        "boss": load_yaml(ROOT / "config" / "platforms" / "boss.yaml"),
        "ats": load_yaml(ROOT / "config" / "platforms" / "ats.yaml"),
        "linkedin": load_yaml(ROOT / "config" / "platforms" / "linkedin.yaml"),
    }
