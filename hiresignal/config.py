"""配置加载：sources.yaml / keywords.yaml。"""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


def load_sources() -> dict:
    with open(CONFIG_DIR / "sources.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_keywords() -> dict:
    with open(CONFIG_DIR / "keywords.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)
