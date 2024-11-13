"""`importmap` management command."""

import json
from pathlib import Path

import httpx
from django.core.management import CommandError
from django_typer.management import TyperCommand, initialize, command

from sonic_importmap.utils import extract_version, get_base_app_name, read_importmap_config, write_importmap_config


class Command(TyperCommand):

    help = "Configure and use importmaps in your Django project."
    endpoint = "https://api.jspm.io/generate"
    importmap_config = {}

    @initialize()
    def init(self):
        # Check if the importmap.config.json exists at the root of a django project
        # if not, creat an empty one
        # If it exists, check if it's a valid JSON file
        if not Path("importmap.config.json").exists():
            write_importmap_config({})
        else:
            try:
                self.importmap_config = read_importmap_config()
            except json.JSONDecodeError:
                raise CommandError("importmap.config.json is not a valid JSON file.")

    @command()
    def add(self, pkg_name: str):
        """Add package to the importmap.config.json file."""

        # Check if the pkg_name already exists in the importmap.config.json file
        if pkg_name in self.importmap_config:
            raise CommandError(
                f"{pkg_name} already exists. Use `update` command to update it."
            )

        response = self.generate_importmap(pkg_name)
        importmap = response.json().get("map").get("imports")

        # Add the pkg_name to the importmap.config.json file
        for name, url in importmap.items():
            version = extract_version(url)
            self.importmap_config[pkg_name] = {
                "name": name,
                "version": version,
                "app_name": get_base_app_name(),
            }

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
            raise CommandError(
                f"Failed to generate importmap for {pkg_name}. Error: {response.text}"
            )
        return response
