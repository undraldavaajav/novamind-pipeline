import json
import re
from datetime import datetime
from pathlib import Path

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text[:60]

def save_json(data, folder, filename):
    Path(folder).mkdir(exist_ok=True)
    path = Path(folder) / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return str(path)

def timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")
