# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import random


class DataSeederConfig(models.Model):
    _name = 'data_seeder.config'
    _description = 'Data Seeder Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    scenario_type = fields.Selection([
        ('sales', 'Sales'),
        ('inventory', 'Inventory'),
        ('purchase', 'Purchase'),
        ('manufacturing', 'Manufacturing'),
    ], string='Scenario Type', default='sales', required=True)

    # Sales scenario settings
    customer_count = fields.Integer(string='Number of Customers', default=10)
    product_count = fields.Integer(string='Number of Products', default=5)
    order_count = fields.Integer(string='Number of Sale Orders', default=20)
    avg_lines_per_order = fields.Integer(string='Average Lines per Order', default=3)

    # Workflow percentages
    percent_confirmed = fields.Integer(string='% Confirmed Orders', default=80, help="Percentage of orders to confirm")
    percent_invoiced = fields.Integer(string='% Invoiced', default=70, help="Percentage of confirmed orders to invoice")
    percent_paid = fields.Integer(string='% Paid', default=60, help="Percentage of invoices to pay")

    # Date range
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    # Company
    company_id = fields.Many2one('res.company', string='Company',
                                  default=lambda self: self.env.company)

    # Price settings
    min_price = fields.Float(string='Minimum Price', default=10.0)
    max_price = fields.Float(string='Maximum Price', default=500.0)
    min_quantity = fields.Integer(string='Minimum Quantity', default=1)
    max_quantity = fields.Integer(string='Maximum Quantity', default=50)

    # Customer settings
    customer_type = fields.Selection([
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('mixed', 'Mixed'),
    ], string='Customer Type', default='mixed')

    # Product settings
    product_type = fields.Selection([
        ('product', 'Storable Product'),
        ('consu', 'Consumable'),
        ('service', 'Service'),
    ], string='Product Type', default='product')

    active = fields.Boolean(string='Active', default=True)
    is_template = fields.Boolean(string='Is Template', default=False)

    _sql_constraints = [
        ('date_check', 'CHECK (date_end >= date_start)',
         'End date must be greater than or equal to start date'),
        ('percent_check', 'CHECK (percent_confirmed <= 100 AND percent_invoiced <= 100 AND percent_paid <= 100)',
         'Percentages must not exceed 100'),
    ]

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.name + ' (Copy)'
        default['is_template'] = False
        return super().copy(default)

    def get_random_date(self):
        """Get a random date within the configured range"""
        start = self.date_start
        end = self.date_end
        delta = (end - start).days
        random_days = random.randint(0, delta)
        return start + timedelta(days=random_days)

    def get_random_amount(self):
        """Get a random amount within the configured price range"""
        return random.uniform(self.min_price, self.max_price)

    def get_random_quantity(self):
        """Get a random quantity within the configured range"""
        return random.randint(self.min_quantity, self.max_quantity)
