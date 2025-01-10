import json

import pytest

from lfp_importmap.templatetags.lfp_importmap import javascript_importmap_tags
from lfp_importmap.utils import get_importmap_config_path


class TestTemplateTag:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        config_path = get_importmap_config_path()
        # Create a test importmap.config.json
        config = {"react": {"name": "react", "version": "18.2.0", "app_name": "test_project"}}
        with open(config_path, "w") as f:
            json.dump(config, f)

        yield

        if config_path.exists():
            config_path.unlink()

    def test_javascript_importmap_tags(self):
        context = javascript_importmap_tags()
        assert "importmap_data" in context
        assert context["importmap_data"]["react"] == "test_project/react.js"
        assert "index_file" in context
        assert context["index_file"] == "test_project/index.js"
