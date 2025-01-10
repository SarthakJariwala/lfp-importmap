import json
import os
import re
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.management import CommandError


def extract_version(url) -> Optional[str]:
    match = re.search(r"@(\d+\.\d+\.\d+)", url)
    return match.group(1) if match else None


def get_static_dir() -> Path:
    return Path(settings.STATIC_ROOT) if settings.STATIC_ROOT else Path(settings.STATICFILES_DIRS[0])


def get_base_app_name() -> str:
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    if settings_module:
        app_name = settings_module.split(".")[0]
        return app_name
    else:
        raise CommandError("DJANGO_SETTINGS_MODULE environment variable not set.")


def get_importmap_config_path() -> Path:
    project_root = settings.BASE_DIR
    return Path(project_root) / "importmap.config.json"


def read_importmap_config() -> dict:
    importmap_config_file = get_importmap_config_path()
    with open(importmap_config_file, "r") as f:
        return json.load(f)


def write_importmap_config(config) -> None:
    importmap_config_file = get_importmap_config_path()
    with open(importmap_config_file, "w") as f:
        json.dump(config, f, indent=4)
