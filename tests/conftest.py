import os
import shutil
from pathlib import Path

from django.conf import settings


def clean_static_directory():
    """Helper function to safely clean static directory"""
    static_dir = Path(settings.STATIC_ROOT)
    try:
        if static_dir.exists():
            shutil.rmtree(static_dir, ignore_errors=True)
    except Exception:
        pass  # Ignore any errors during cleanup


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
        STATIC_ROOT=str(BASE_DIR / "static"),
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        SECRET_KEY="test-key",
    )


def pytest_sessionstart():
    # Clean up static directory at the start of test session
    clean_static_directory()


def pytest_sessionfinish():
    # Clean up static directory at the end of test session
    clean_static_directory()
