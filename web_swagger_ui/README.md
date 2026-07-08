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

## Notes for other developers

- Keep request-body schemas in the API module that owns the endpoint.
- If you add a new API controller in your custom addon, it will appear in Swagger automatically as long as its route starts with one of the configured prefixes.
- If you need better schema details, add explicit request-body metadata in the controller module that defines the endpoint.
