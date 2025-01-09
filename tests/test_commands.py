import json
from pathlib import Path
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from lfp_importmap.utils import get_importmap_config_path

from .conftest import clean_static_directory


class TestImportmapCommand:
    def setup_method(self):
        # Create temporary importmap.config.json for testing
        self.config_path = Path(get_importmap_config_path())
        if self.config_path.exists():
            self.config_path.unlink()
        clean_static_directory()

    def teardown_method(self):
        # Clean up after tests
        if self.config_path.exists():
            self.config_path.unlink()
        clean_static_directory()

    @patch("httpx.post")
    def test_add_package(self, mock_post):
        # Mock the JSPM API response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "map": {"imports": {"react": "https://ga.jspm.io/npm:react@18.2.0/index.js"}}
        }

        call_command("importmap", "add", "react")

        assert self.config_path.exists()

        # Verify the config file was created with correct content
        with open(self.config_path) as f:
            config = json.load(f)
            assert "react" in config
            assert config["react"]["version"] == "18.2.0"
            assert config["react"]["app_name"] == "test_project"

    def test_package_already_exists(self):
        # Create a config file with react package
        with open(self.config_path, "w") as f:
            f.write('{"react": {"name": "react", "version": "18.2.0", "app_name": "test_project"}}')

        # Try to add react package again
        with pytest.raises(CommandError):
            call_command("importmap", "add", "react")

    @patch("httpx.post")
    def test_generate_importmap_error(self, mock_post):
        # Mock the JSPM API response
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Error: Something went wrong on JSPM side"

        # Try to add react package
        with pytest.raises(CommandError):
            call_command("importmap", "add", "react")
