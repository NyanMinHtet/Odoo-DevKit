# -*- coding: utf-8 -*-

from odoo import _, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class DataSeederRunManager(models.AbstractModel):
    _name = 'data_seeder.run.manager'
    _description = 'Data Seeder Run Manager Service'

    def _check_test_database(self):
        """Cleanup is only allowed for test databases."""
        db_name = self.env.cr.dbname
        test_keywords = ['test', 'sandbox', 'dev', 'stage', 'demo', 'tmp']
        if not any(keyword in db_name.lower() for keyword in test_keywords):
            raise ValidationError(_(
                "Run cleanup is only allowed in test/sandbox databases.\n\nCurrent database: %s"
            ) % db_name)

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
            self._check_test_database()

            done_pickings = run.generated_picking_ids.filtered(lambda picking: picking.state == 'done')
            if done_pickings:
                raise ValidationError(_(
                    "Cleanup for runs with validated deliveries is blocked.\n\n"
                    "Create stock returns for delivered pickings before deleting generated records."
                ))

            payments = run.generated_payment_ids
            invoices = run.generated_invoice_ids
            pickings = run.generated_picking_ids
            orders = run.generated_order_ids
            products = run.generated_product_ids
            customers = run.generated_customer_ids

            if payments:
                payments.filtered(lambda payment: payment.state != 'cancel').action_cancel()
                payments.unlink()

            if invoices:
                posted_invoices = invoices.filtered(lambda move: move.state == 'posted')
                if posted_invoices:
                    posted_invoices.button_draft()
                cancellable_invoices = invoices.filtered(lambda move: move.state != 'cancel')
                if cancellable_invoices:
                    cancellable_invoices.button_cancel()
                invoices.unlink()

            if pickings:
                pickings.filtered(lambda picking: picking.state != 'cancel').action_cancel()
                pickings.unlink()

            if orders:
                orders.filtered(lambda order: order.state != 'cancel').action_cancel()
                orders.unlink()

            if products:
                self._clear_generated_inventory(products)
                products.unlink()

            if customers:
                customers.unlink()

        run.unlink()
        return True

    def _clear_generated_inventory(self, products):
        """Remove internal stock left behind for generated tracked goods."""
        storable_products = products.filtered('is_storable')
        if not storable_products:
            return

        quants = self.env['stock.quant'].search([
            ('product_id', 'in', storable_products.ids),
            ('location_id.usage', '=', 'internal'),
            ('quantity', '!=', 0),
        ])
        for quant in quants:
            self.env['stock.quant']._update_available_quantity(
                quant.product_id,
                quant.location_id,
                -quant.quantity,
                lot_id=quant.lot_id,
                package_id=quant.package_id,
                owner_id=quant.owner_id,
            )

    def get_all_runs(self, limit=100):
        """Get all runs"""
        return self.env['data_seeder.run'].search([], limit=limit, order='create_date desc')
