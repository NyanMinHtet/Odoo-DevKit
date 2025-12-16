# -*- coding: utf-8 -*-
{
    'name': 'Swagger UI',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'author': 'Shoto',
    'license': 'LGPL-3',
    'description': """
        This module integrates Swagger UI into Odoo to provide a user-friendly interface for API documentation.
    """,
    'depends': ['base', 'web'],
    'data': [
        'views/swagger_ui_template.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
