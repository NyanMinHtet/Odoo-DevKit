# -*- coding: utf-8 -*-

from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class DataSeederRunManager(models.AbstractModel):
    _name = 'data_seeder.run.manager'
    _description = 'Data Seeder Run Manager Service'

    def create_run(self, config, result):
        """Create a new run record after generation"""
        run = self.env['data_seeder.run'].create({
            'name': f"Data Seeder Run {len(self.env['data_seeder.run']) + 1}",
            'scenario_type': config.get('scenario_type', 'sales'),
            'state': 'done',
            'config_json': str(config),
            'customer_count': result.get('customer_count', 0),
            'product_count': result.get('product_count', 0),
            'order_count': result.get('order_count', 0),
            'invoice_count': result.get('invoice_count', 0),
            'payment_count': result.get('payment_count', 0),
            'execution_time': result.get('execution_time', 0),
            'log': result.get('log', ''),
        })
        return run

    def get_run_summary(self, run_id):
        """Get summary of a run"""
        run = self.env['data_seeder.run'].browse(run_id)
        if not run.exists():
            return None

        return {
            'name': run.name,
            'state': run.state,
            'total_records': run.total_records,
            'execution_time': run.execution_time,
            'created_date': run.create_date,
        }

    def cleanup_run(self, run_id, delete_generated_records=False):
        """Cleanup a run, optionally deleting generated records"""
        run = self.env['data_seeder.run'].browse(run_id)
        if not run.exists():
            return False

        if delete_generated_records:
            # Delete generated records
            self.env['account.payment'].browse(run.generated_payment_ids).unlink()
            self.env['account.move'].browse(run.generated_invoice_ids).unlink()
            self.env['sale.order'].browse(run.generated_order_ids).unlink()
            self.env['product.product'].browse(run.generated_product_ids).unlink()
            self.env['res.partner'].browse(run.generated_customer_ids).unlink()

        run.unlink()
        return True

    def get_all_runs(self, limit=100):
        """Get all runs"""
        return self.env['data_seeder.run'].search([], limit=limit, order='create_date desc')
