import os
from pathlib import Path

from django.conf import settings


def pytest_configure():
    BASE_DIR = Path(__file__).resolve().parent
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
    settings.configure(
        DEBUG=True,
        BASE_DIR=BASE_DIR,
        INSTALLED_APPS=[
            "django.contrib.staticfiles",
            "lfp_importmap",
        ],
        STATIC_URL="/static/",
        STATIC_ROOT="static",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        SECRET_KEY="test-key",
    )
