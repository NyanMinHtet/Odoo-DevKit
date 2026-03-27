# -*- coding: utf-8 -*-
{
    'name': 'Odoo Data Seeder',
    'version': '18.0.2.0.0',
    'category': 'Developer Tools',
    'summary': 'Generate linked test data and simulate sales-to-delivery workflows safely',
    'description': """
Odoo Data Seeder
================
Generate realistic business records in safe test databases and simulate linked workflows.

Main features:
- Sales dataset generation for customers, products, and sale orders
- Workflow execution for confirmations, invoices, payments, and deliveries
- Inventory-aware product generation with optional stock seeding
- Generation history with linked records and execution logs
- Test database safety checks and cleanup support
""",
    'author': 'Shoto',
    'website': 'https://nyanminhtet-portfolio.netlify.app',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'sale_stock',
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/run_views.xml',
        'wizard/wizard_views.xml',
        'data/default_scenarios.xml',
        'views/menu.xml',
    ],
    'images': [
        'static/description/img.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
