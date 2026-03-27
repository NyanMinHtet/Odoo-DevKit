# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class DataSeederWizard(models.TransientModel):
    _name = 'data_seeder.wizard'
    _description = 'Data Seeder Wizard'

    # Basic settings
    customer_count = fields.Integer(string='Number of Customers', default=10, required=True)
    product_count = fields.Integer(string='Number of Products', default=5, required=True)
    order_count = fields.Integer(string='Number of Sale Orders', default=20, required=True)
    avg_lines_per_order = fields.Integer(string='Average Lines per Order', default=3, required=True)

    # Workflow percentages
    percent_confirmed = fields.Integer(string='% Confirmed Orders', default=80, required=True)
    percent_invoiced = fields.Integer(string='% Invoiced', default=70, required=True)
    percent_paid = fields.Integer(string='% Paid', default=60, required=True)
    percent_delivered = fields.Integer(string='% Delivered', default=80, required=True)

    # Date range
    date_start = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    date_end = fields.Date(string='End Date', required=True, default=lambda self: fields.Date.context_today(self) + timedelta(days=30))

    # Pricing
    min_price = fields.Float(string='Minimum Price', default=10.0)
    max_price = fields.Float(string='Maximum Price', default=500.0)
    min_quantity = fields.Integer(string='Minimum Quantity', default=1)
    max_quantity = fields.Integer(string='Maximum Quantity', default=50)
    initial_stock_per_product = fields.Integer(string='Initial Stock Per Product', default=25)

    # Inventory
    enable_inventory_flow = fields.Boolean(string='Enable Inventory Flow', default=False)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        default=lambda self: self.env['stock.warehouse'].search([
            '|', ('company_id', '=', False), ('company_id', '=', self.env.company.id),
        ], limit=1),
    )
    stock_location_id = fields.Many2one(
        'stock.location',
        string='Stock Location',
        domain="[('usage', '=', 'internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    storable_product_ratio = fields.Integer(string='Storable Product Ratio', default=70)

    # Company
    company_id = fields.Many2one('res.company', string='Company',
                                  default=lambda self: self.env.company)

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], default='draft')

    log = fields.Text(string='Log')

    def _check_test_database(self):
        """Check if we're in a test/sandbox database"""
        db_name = self.env.cr.dbname
        # Allow databases containing 'test', 'sandbox', 'dev', 'stage', 'demo'
        test_keywords = ['test', 'sandbox', 'dev', 'stage', 'demo', 'tmp']
        is_test_db = any(keyword in db_name.lower() for keyword in test_keywords)

        if not is_test_db:
            raise ValidationError(_(
                "Data Seeder is only allowed in test/sandbox databases.\n\n"
                "Current database: %s\n\n"
                "To enable generation, rename your database to include keywords like:\n"
                "- test, sandbox, dev, stage, or demo"
            ) % db_name)

    def _check_max_limits(self):
        """Check if generation request exceeds safe limits"""
        max_customers = 1000
        max_products = 500
        max_orders = 5000

        if self.customer_count > max_customers:
            raise ValidationError(_("Customer count cannot exceed %d") % max_customers)
        if self.product_count > max_products:
            raise ValidationError(_("Product count cannot exceed %d") % max_products)
        if self.order_count > max_orders:
            raise ValidationError(_("Order count cannot exceed %d") % max_orders)

    def _check_date_range(self):
        """Validate date range configuration."""
        if self.date_end < self.date_start:
            raise ValidationError(_("End date cannot be earlier than start date."))

    def _check_percentages(self):
        """Validate percentage-based workflow settings."""
        percentage_fields = [
            ('percent_confirmed', _('Confirmed percentage')),
            ('percent_invoiced', _('Invoiced percentage')),
            ('percent_paid', _('Paid percentage')),
            ('percent_delivered', _('Delivered percentage')),
            ('storable_product_ratio', _('Storable product ratio')),
        ]
        for field_name, field_label in percentage_fields:
            value = self[field_name]
            if value < 0 or value > 100:
                raise ValidationError(_("%s must be between 0 and 100.") % field_label)

    def _check_inventory_settings(self):
        """Validate inventory-related configuration."""
        if self.initial_stock_per_product < 0:
            raise ValidationError(_("Initial stock per product cannot be negative."))
        if self.enable_inventory_flow and not self.warehouse_id:
            raise ValidationError(_("A warehouse is required when inventory flow is enabled."))

    def action_start_generation(self):
        """Validate and start data generation"""
        try:
            self._check_test_database()
            self._check_max_limits()
            self._check_date_range()
            self._check_percentages()
            self._check_inventory_settings()
        except ValidationError as e:
            raise e

        self.write({'state': 'running', 'log': 'Starting generation...\n'})

        # Create run record
        run = self.env['data_seeder.run'].create({
            'name': f"Data Seeder Run {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            'scenario_type': 'sales',
            'state': 'running',
            'start_date': fields.Datetime.now(),
            'config_json': str(self.read()[0]),
            'company_id': self.company_id.id,
        })

        try:
            params = {
                'customer_count': self.customer_count,
                'product_count': self.product_count,
                'order_count': self.order_count,
                'avg_lines': self.avg_lines_per_order,
                'percent_confirmed': self.percent_confirmed,
                'percent_invoiced': self.percent_invoiced,
                'percent_paid': self.percent_paid,
                'percent_delivered': self.percent_delivered,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'min_price': self.min_price,
                'max_price': self.max_price,
                'min_quantity': self.min_quantity,
                'max_quantity': self.max_quantity,
                'initial_stock_per_product': self.initial_stock_per_product,
                'company_id': self.company_id.id,
                'enable_inventory_flow': self.enable_inventory_flow,
                'warehouse_id': self.warehouse_id.id,
                'stock_location_id': self.stock_location_id.id,
                'storable_product_ratio': self.storable_product_ratio,
                'run_id': run.id,
            }

            # Run generation service
            result = self.env['data_seeder.data.generator'].generate(params)

            # Update run record
            run.write({
                'state': 'done',
                'end_date': fields.Datetime.now(),
                'customer_count': result.get('customer_count', 0),
                'product_count': result.get('product_count', 0),
                'order_count': result.get('order_count', 0),
                'invoice_count': result.get('invoice_count', 0),
                'payment_count': result.get('payment_count', 0),
                'execution_time': result.get('execution_time', 0),
                'log': result.get('log', ''),
            })

            self.write({
                'state': 'done',
                'log': f"Generation completed successfully!\n\n"
                       f"Customers: {result.get('customer_count', 0)}\n"
                       f"Products: {result.get('product_count', 0)}\n"
                       f"Orders: {result.get('order_count', 0)}\n"
                       f"Invoices: {result.get('invoice_count', 0)}\n"
                       f"Payments: {result.get('payment_count', 0)}\n"
                       f"Execution time: {result.get('execution_time', 0):.2f}s"
            })

            return {
                'type': 'ir.actions.act_window',
                'name': _('Generation Complete'),
                'res_model': 'data_seeder.run',
                'view_mode': 'form',
                'res_id': run.id,
                'target': 'current',
            }

        except Exception as e:
            _logger.exception("Generation failed")
            run.write({
                'state': 'error',
                'end_date': fields.Datetime.now(),
                'error_message': str(e),
            })
            self.write({
                'state': 'error',
                'log': f"Error: {str(e)}",
            })
            raise UserError(_("Generation failed: %s") % str(e))

    def action_cancel(self):
        self.write({'state': 'error', 'log': 'Cancelled by user'})
        return {'type': 'ir.actions.act_window.close'}
