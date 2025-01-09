from django import template

from lfp_importmap.utils import get_base_app_name, read_importmap_config

register = template.Library()


@register.inclusion_tag("lfp_importmap/javascript_importmap_tags.html")
def javascript_importmap_tags():
    # Get the index file name where imports are defined
    base_app_name = get_base_app_name()
    index_file = f"{base_app_name}/index.js"

    importmap_data = read_importmap_config()
    processed_import_data = {
        data["name"]: f"{data['app_name']}/{package}.js" for package, data in importmap_data.items()
    }

    return {"importmap_data": processed_import_data, "index_file": index_file}
