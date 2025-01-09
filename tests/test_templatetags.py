import json

from django.conf import settings

from sonic_importmap.templatetags.sonic_importmap import javascript_importmap_tags


class TestTemplateTag:
    def setup_method(self):
        self.config_path = settings.BASE_DIR / "importmap.config.json"
        # Create a test importmap.config.json
        config = {"react": {"name": "react", "version": "18.2.0", "app_name": "test_app"}}
        with open(self.config_path, "w") as f:
            json.dump(config, f)

    def teardown_method(self):
        if self.config_path.exists():
            self.config_path.unlink()

    def test_javascript_importmap_tags(self):
        context = javascript_importmap_tags()
        assert "importmap_data" in context
        assert context["importmap_data"]["react"] == "test_app/react.js"
