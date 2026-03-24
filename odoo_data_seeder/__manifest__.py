# -*- coding: utf-8 -*-
{
    'name': 'Odoo Data Seeder',
    'version': '18.0.1.0.0',
    'category': 'Developer Tools',
    'summary': 'Generate realistic, linked business data and simulate workflows inside a test database',
    'description': """
Odoo Data Seeder
================
Enable Odoo developers to:
* Generate realistic data instantly
* Simulate real business workflows
* Test reports, dashboards, and performance
* Avoid manual data entry and CSV imports

Core Features:
- Select scenario → Configure → Generate → Get full working dataset
- Sales scenario support (customers, products, orders, invoices, payments)
- Workflow simulation (confirm orders, create invoices, register payments)
- Run management with execution logs
- Safety checks for test database
""",
    'author': 'shoto', 'website': 'https://github.com/nyanminhtet/odoo-devkit',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/run_views.xml',
        'wizard/wizard_views.xml',
        'data/default_scenarios.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
