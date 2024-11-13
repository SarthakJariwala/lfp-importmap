import json
import os
import re

from django.core.management import CommandError


def extract_version(url):
    match = re.search(r'@(\d+\.\d+\.\d+)', url)
    return match.group(1) if match else None


def get_base_app_name():
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    if settings_module:
        app_name = settings_module.split(".")[0]
        return app_name
    else:
        raise CommandError("DJANGO_SETTINGS_MODULE environment variable not set.")


def read_importmap_config():
    with open("importmap.config.json", "r") as f:
        return json.load(f)


def write_importmap_config(config):
    with open("importmap.config.json", "w") as f:
        json.dump(config, f, indent=4)
