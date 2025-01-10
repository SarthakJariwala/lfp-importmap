import json
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from lfp_importmap.utils import get_importmap_config_path, get_static_dir, write_importmap_config

from .conftest import clean_static_directory


class TestImportmapCommand:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        # Create temporary importmap.config.json for testing
        self.config_path = get_importmap_config_path()
        if self.config_path.exists():
            self.config_path.unlink()
        clean_static_directory()
        write_importmap_config({})

        yield

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

    def test_init_creates_config_file(self):
        """Test that init creates config file if it doesn't exist."""
        if self.config_path.exists():
            self.config_path.unlink()

        call_command("importmap")
        assert self.config_path.exists()
        with open(self.config_path) as file:
            assert json.load(file) == {}

    def test_init_invalid_json(self):
        """Test that init raises error for invalid JSON."""
        with open(self.config_path, "w") as f:
            f.write("invalid json")

        with pytest.raises(CommandError) as exc_info:
            call_command("importmap")
            assert str(exc_info.value) == "importmap.config.json is not a valid JSON file"

    @patch("httpx.get")
    @patch("httpx.post")
    def test_vendor_package_download_error(self, mock_post, mock_get):
        """Test error handling when package download fails."""
        # Mock JSPM API success
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "map": {"imports": {"react": "https://ga.jspm.io/npm:react@18.2.0/index.js"}}
        }

        # Mock package download failure
        mock_get.return_value.status_code = 404
        mock_get.return_value.text = "Not Found"

        with pytest.raises(CommandError) as exc_info:
            call_command("importmap", "add", "react")
            assert (
                str(exc_info.value)
                == "Failed to download file from https://ga.jspm.io/npm:react@18.2.0/index.js. Error: Not Found"
            )

    @patch("httpx.get")
    @patch("httpx.post")
    def test_creates_index_file(self, mock_post, mock_get):
        """Test that add command creates index.js if it doesn't exist."""
        # Mock successful responses
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "map": {"imports": {"react": "https://ga.jspm.io/npm:react@18.2.0/index.js"}}
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "console.log('react');"

        call_command("importmap", "add", "react")

        index_path = get_static_dir() / "test_project" / "index.js"
        assert index_path.exists()
        content = index_path.read_text()
        assert 'import "react";' in content

    @patch("httpx.get")
    @patch("httpx.post")
    def test_avoid_duplicate_imports(self, mock_post, mock_get):
        """Test that import statements aren't duplicated in index.js."""
        # Mock successful responses
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "map": {"imports": {"react": "https://ga.jspm.io/npm:react@18.2.0/index.js"}}
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "console.log('react');"

        # Create index.js with existing import
        index_dir = get_static_dir() / "test_project"
        index_dir.mkdir(parents=True, exist_ok=True)
        index_path = index_dir / "index.js"
        index_path.write_text('import "react";\n')

        call_command("importmap", "add", "react")

        content = index_path.read_text()
        assert content.count('import "react";') == 1

    @patch("httpx.post")
    def test_generate_importmap_error(self, mock_post):
        # Mock the JSPM API response
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Error: Something went wrong on JSPM side"

        # Try to add react package
        with pytest.raises(CommandError):
            call_command("importmap", "add", "react")

    # Local JS files
    def test_add_local_file(self):
        """Test adding a local JS file to importmap."""

        call_command("importmap", "add", "app.js", local=True)

        assert self.config_path.exists()

        # Verify the config file was created with correct content
        with open(self.config_path) as f:
            config = json.load(f)
            assert "app" in config
            assert config["app"]["version"] is None
            assert config["app"]["app_name"] == "test_project"

        # Check that import was added to index.js
        index_path = get_static_dir() / "test_project" / "index.js"
        assert index_path.exists()
        content = index_path.read_text()
        assert 'import "app";' in content
