import os
import json
from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag("sonic_importmap/javascript_importmap_tags.html")
def javascript_importmap_tags():
    project_root = settings.BASE_DIR  
    config_path = os.path.join(project_root, 'importmap.config.json')

    with open(config_path, 'r') as config_file:
        importmap_data = json.load(config_file)

    processed_import_data = {
        data["name"]: f"{data['app_name']}/{package}.js"
        for package, data in importmap_data.items()
    }

    return {"importmap_data": processed_import_data}