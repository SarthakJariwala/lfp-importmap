"""`importmap` management command."""

import json
from pathlib import Path

import httpx
from django.core.management import CommandError
from django_typer.management import TyperCommand, command, initialize

from lfp_importmap.utils import (
    extract_version,
    get_base_app_name,
    get_importmap_config_path,
    get_static_dir,
    read_importmap_config,
    write_importmap_config,
)


class Command(TyperCommand):
    help = "Configure and use importmaps in your Django project."
    endpoint = "https://api.jspm.io/generate"
    importmap_config = {}

    @initialize(invoke_without_command=True)
    def init(self) -> None:
        # Check if the importmap.config.json exists at the root of a django project
        # if not, create an empty one
        # If it exists, check if it's a valid JSON file
        if not get_importmap_config_path().exists():
            write_importmap_config({})
        else:
            try:
                self.importmap_config = read_importmap_config()
            except json.JSONDecodeError:
                raise CommandError("importmap.config.json is not a valid JSON file.")

    @command()
    def add(self, pkg_name: str) -> None:
        """Add package to the importmap.config.json file."""

        # Check if the pkg_name already exists in the importmap.config.json file
        if pkg_name in self.importmap_config:
            raise CommandError(f"{pkg_name} already exists. Use `update` command to update it.")

        response = self.generate_importmap(pkg_name)
        importmap = response.json().get("map").get("imports")

        app_name = get_base_app_name()

        # Add the pkg_name to the importmap.config.json file
        for name, url in importmap.items():
            version = extract_version(url)
            self.importmap_config[pkg_name] = {
                "name": name,
                "version": version,
                "app_name": app_name,
            }
            self.vendor_package(url, app_name, f"{name}.js")
            self.add_import_to_index(name, app_name)

        write_importmap_config(self.importmap_config)

    def generate_importmap(self, pkg_name: str) -> httpx.Response:
        """Generate importmap for a package."""
        response = httpx.post(
            self.endpoint,
            json={
                "install": pkg_name,
                "env": ["browser", "production", "module"],
            },
        )
        if response.status_code != httpx.codes.OK:
            raise CommandError(f"Failed to generate importmap for {pkg_name}. Error: {response.text}")
        return response

    def vendor_package(self, url: str, app_name: str, file_name: str) -> None:
        """Vendor a package by downloading it and saving to static directory."""

        response = httpx.get(url)
        if response.status_code != httpx.codes.OK:
            raise CommandError(f"Failed to download file from {url}. Error: {response.text}")

        app_dir = self._get_or_create_app_dir(app_name)

        file_path = app_dir / file_name
        file_path.write_text(response.text)

    def add_import_to_index(self, name: str, app_name: str) -> None:
        """Add import statement to index.js."""
        app_dir = self._get_or_create_app_dir(app_name)

        index_path = app_dir / "index.js"
        if not index_path.exists():
            index_path.touch()

        content = index_path.read_text()
        import_statement = f'import "{name}";\n'
        if import_statement not in content:
            with open(index_path, "a") as f:
                f.write(import_statement)

    def _get_or_create_app_dir(self, app_name: str) -> Path:
        static_dir = get_static_dir()
        app_dir = static_dir / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
