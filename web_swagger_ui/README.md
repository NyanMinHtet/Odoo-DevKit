# Swagger UI Module for Odoo

This module integrates Swagger UI into your Odoo project to provide a user-friendly interface for your API documentation.

## File Structure

```
/web_swagger_ui/
├───__init__.py
├───__manifest__.py
├───controllers/
│   ├───__init__.py
│   └───main.py
├───static/
│   └───src/
│       ├───lib/
│       │   └───swagger-ui/
│       │       ├───swagger-ui-bundle.js
│       │       ├───swagger-ui-standalone-preset.js
│       │       └───swagger-ui.css
│       └───swagger.json
└───views/
    └───swagger_ui_template.xml
```

## How to Use It

1.  **Restart your Odoo server:** This is necessary for Odoo to recognize the new module.

2.  **Update the apps list:**
    *   Go to the **Apps** menu in your Odoo dashboard.
    *   Click on **Update Apps List**.
    *   You might need to remove the default "Apps" filter in the search bar to see all modules.

3.  **Install the module:**
    *   Search for "Swagger UI" and install it.

4.  **Access Swagger UI:**
    *   After installation, a new menu item, "Swagger UI," will appear under the **Settings** menu. Click on **API Documentation** to open the Swagger UI page in a new tab.

5.  **Customize your API specification:**
    *   The Swagger UI will display a sample API documentation. To use your own API specification, you need to replace the content of the following file with your own [OpenAPI 3.0](https://swagger.io/specification/) compliant JSON:
        `web_swagger_ui/static/src/swagger.json`
