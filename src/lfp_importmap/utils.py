import json
import os
import re

from django.conf import settings
from django.core.management import CommandError


def extract_version(url):
    match = re.search(r"@(\d+\.\d+\.\d+)", url)
    return match.group(1) if match else None


def get_base_app_name():
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    if settings_module:
        app_name = settings_module.split(".")[0]
        return app_name
    else:
        raise CommandError("DJANGO_SETTINGS_MODULE environment variable not set.")


def get_importmap_config_path():
    project_root = settings.BASE_DIR
    return os.path.join(project_root, "importmap.config.json")


def read_importmap_config():
    importmap_config_file = get_importmap_config_path()
    with open(importmap_config_file, "r") as f:
        return json.load(f)


def write_importmap_config(config):
    importmap_config_file = get_importmap_config_path()
    with open(importmap_config_file, "w") as f:
        json.dump(config, f, indent=4)
