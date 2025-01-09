import os

import pytest
from django.core.management import CommandError

from lfp_importmap.utils import extract_version, get_base_app_name


def test_extract_version():
    url = "https://ga.jspm.io/npm:react@18.2.0/index.js"
    assert extract_version(url) == "18.2.0"


def test_extract_version_no_match():
    url = "https://example.com/react/index.js"
    assert extract_version(url) is None


def test_get_base_app_name_error_without_settings_module():
    # Save original environment variable
    original_settings = os.environ.get("DJANGO_SETTINGS_MODULE")
    # Remove the environment variable
    if "DJANGO_SETTINGS_MODULE" in os.environ:
        del os.environ["DJANGO_SETTINGS_MODULE"]

    try:
        with pytest.raises(CommandError):
            get_base_app_name()
    finally:
        # Restore original environment variable
        if original_settings:
            os.environ["DJANGO_SETTINGS_MODULE"] = original_settings


def test_get_base_app_name():
    assert get_base_app_name() == "test_project"
