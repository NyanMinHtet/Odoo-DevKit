# Swagger UI Module for Odoo

This module integrates Swagger UI into your Odoo project and generates an OpenAPI document from the installed Odoo HTTP routes. It is designed to work well with custom API modules such as fs_connector.

## What it does

- Serves a Swagger UI page at `/swagger/ui`
- Generates an OpenAPI document at `/swagger/openapi.json`
- Includes all routes whose URL starts with one or more configured API prefixes
- Works with multiple prefixes, so you can document several API areas at once

## File Structure

```
/web_swagger_ui/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── static/
│   └── src/
│       ├── lib/
│       │   └── swagger-ui/
│       │       ├── swagger-ui-bundle.js
│       │       ├── swagger-ui-standalone-preset.js
│       │       └── swagger-ui.css
└── views/
    └── swagger_ui_template.xml
```

## How to use it

1. Restart your Odoo server.
2. Update the apps list and install the module.
3. Open the Swagger UI page at `/swagger/ui`.
4. The OpenAPI document is generated dynamically from the installed routes.

## Configuring API prefixes

By default, the module documents routes under `/fs/api`.

To add more prefixes or change the current ones:

1. Go to Settings > Technical > Parameters > System Parameters.
2. Create or update a system parameter with this key:
   - `web_swagger_ui.api_prefixes`
3. Set the value as a comma-separated list, for example:
   - `/fs/api,/api/jo,/custom/api`

The generator will include every route whose path begins with any configured prefix.

## Using swagger_request_body

If you want Swagger to show a better request body for your endpoint, define the schema in the same controller module that owns the route.

Example:

```python
# -*- coding: utf-8 -*-
from odoo import http
from .utils import json_response, parse_http_payload


def swagger_request_body(schema=None):
    def decorator(func):
        func.swagger_request_body = schema or {
            'type': 'object',
            'properties': {},
            'additionalProperties': True,
        }
        return func
    return decorator


class MyApiController(http.Controller):
    @http.route('/my/api/create', type='http', auth='none', methods=['POST'], csrf=False)
    @swagger_request_body(
        {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'email': {'type': 'string'},
                'age': {'type': 'integer'},
            },
            'required': ['name'],
        }
    )
    def create_record(self, **_kwargs):
        payload, error = parse_http_payload()
        if error:
            return error
        return json_response(status=200, data={'ok': True})
```

### Rules for developers

- Put the decorator in the module that defines the endpoint.
- Use it only for endpoints you want Swagger to describe more clearly.
- Keep the route path under one of the configured API prefixes so it appears in the generated OpenAPI document.
- If you add a new API controller in your custom addon, it will appear in Swagger automatically as long as its route starts with one of the configured prefixes.
