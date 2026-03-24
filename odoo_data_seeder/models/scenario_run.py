# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class DataSeederRun(models.Model):
    _name = 'data_seeder.run'
    _description = 'Data Seeder Run'
    _order = 'create_date desc'

    name = fields.Char(string='Run Name', required=True)
    scenario_type = fields.Char(string='Scenario Type', default='sales')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], string='Status', default='draft', required=True)

    # Configuration snapshot
    config_json = fields.Text(string='Configuration')

    # Record counts
    customer_count = fields.Integer(string='Customers Generated', default=0)
    product_count = fields.Integer(string='Products Generated', default=0)
    order_count = fields.Integer(string='Orders Generated', default=0)
    invoice_count = fields.Integer(string='Invoices Generated', default=0)
    payment_count = fields.Integer(string='Payments Registered', default=0)

    # Execution metrics
    start_date = fields.Datetime(string='Start Time')
    end_date = fields.Datetime(string='End Time')
    execution_time = fields.Float(string='Execution Time (seconds)')

    # Logs and results
    log = fields.Text(string='Execution Log')
    error_message = fields.Text(string='Error Message')

    # Generated records tracking
    generated_customer_ids = fields.Many2many('res.partner', string='Generated Customers')
    generated_product_ids = fields.Many2many('product.product', string='Generated Products')
    generated_order_ids = fields.Many2many('sale.order', string='Generated Orders')
    generated_invoice_ids = fields.Many2many('account.move', string='Generated Invoices')

    company_id = fields.Many2many('res.company', string='Company')

    def action_view_generated_records(self):
        """Open tree view of all generated records"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Records'),
            'res_model': 'data_seeder.run.record.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_run_id': self.id,
            }
        }

    def action_cancel(self):
        self.write({'state': 'error', 'error_message': 'Cancelled by user'})

    def _compute_total_records(self):
        for rec in self:
            rec.total_records = (
                rec.customer_count +
                rec.product_count +
                rec.order_count +
                rec.invoice_count +
                rec.payment_count
            )

    total_records = fields.Integer(string='Total Records', compute='_compute_total_records')
