from main import IMAGE_TARGET_TEMPLATES
from mako.lookup import TemplateLookup
pages = {
    "static/pages/image.html": {
        "template_name": "image.html",
        "template_inputs": {
            "API_URL_BASE": "/api",
            "STATIC_PATH": "/static",
            "TARGET_TYPE": "image",
            "TARGET_TEMPLATES": IMAGE_TARGET_TEMPLATES
        }
    },
    "static/pages/video.html": {
        "template_name": "video.html",
        "template_inputs": {
            "API_URL_BASE": "/api",
            "STATIC_PATH": "/static",
            "TARGET_TYPE": "video",
            "TARGET_TEMPLATES": IMAGE_TARGET_TEMPLATES
        }
    }
}

lookup = TemplateLookup(directories=["./templates"])
for page_path, data in pages.items():
    print(data)
    template = lookup.get_template(data["template_name"])
    template_result = template.render(**data["template_inputs"])
    with open(page_path, "w+") as f:
        f.write(template_result)
