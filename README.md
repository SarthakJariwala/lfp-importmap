# lfp-importmap

A simple way to use Javascript `importmaps` in your Django projects.

## What can you do with it?

Use Javascript libraries in your Django projects without having to install `node` and related tooling.
No frontend build system required!

## How to use it?

1. Add `lfp_importmap` to your `INSTALLED_APPS` in your `settings.py`

```python
INSTALLED_APPS = [
    ...
    'lfp_importmap',
]
```

2. Add any JS library using the new management command:

```bash
python manage.py importmap add htmx.org
```

This will create an `importmap.config.json` file in your project root.
It will also vendor the package code and make it available in your templates.

3. In your `base.html` template, add the following:

```html
{% load lfp_importmap %}

<html>
  <head>
    ... {% javascript_importmap_tags %}
  </head>
  <body>
    ...
  </body>
</html>
```

4. That's it! The module is now ready for use in your templates.

Continuing the example from above, you can now use the `htmx` module in your templates:

```html
<button hx-get="{% url 'my-url-name' %}">Click me</button>
```

## LICENSE

MIT
