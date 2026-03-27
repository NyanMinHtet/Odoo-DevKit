# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestDataSeeder(TransactionCase):

    def _wizard_vals(self, **overrides):
        today = fields.Date.today()
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id),
        ], limit=1)
        vals = {
            'customer_count': 2,
            'product_count': 2,
            'order_count': 3,
            'avg_lines_per_order': 1,
            'percent_confirmed': 100,
            'percent_invoiced': 0,
            'percent_paid': 0,
            'percent_delivered': 0,
            'date_start': today,
            'date_end': today + timedelta(days=7),
            'min_price': 10.0,
            'max_price': 20.0,
            'min_quantity': 1,
            'max_quantity': 3,
            'initial_stock_per_product': 25,
            'enable_inventory_flow': False,
            'warehouse_id': warehouse.id,
            'stock_location_id': warehouse.lot_stock_id.id,
            'storable_product_ratio': 70,
            'company_id': self.env.company.id,
        }
        vals.update(overrides)
        return vals

    def test_default_scenarios_loaded(self):
        default_sales = self.env.ref('odoo_data_seeder.default_sales_scenario')
        small_test = self.env.ref('odoo_data_seeder.small_test_scenario')
        large_perf = self.env.ref('odoo_data_seeder.large_performance_scenario')

        self.assertEqual(default_sales.customer_count, 50)
        self.assertEqual(default_sales.product_count, 10)
        self.assertEqual(default_sales.order_count, 100)
        self.assertTrue(default_sales.is_template)

        self.assertEqual(small_test.customer_count, 10)
        self.assertEqual(small_test.product_count, 5)
        self.assertEqual(small_test.order_count, 20)
        self.assertTrue(small_test.is_template)

        self.assertEqual(large_perf.customer_count, 500)
        self.assertEqual(large_perf.product_count, 50)
        self.assertEqual(large_perf.order_count, 2000)
        self.assertTrue(large_perf.is_template)

    def test_wizard_max_limits_validation(self):
        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals(customer_count=1001))
        with self.assertRaises(ValidationError):
            wiz._check_max_limits()

        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals(product_count=501))
        with self.assertRaises(ValidationError):
            wiz._check_max_limits()

        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals(order_count=5001))
        with self.assertRaises(ValidationError):
            wiz._check_max_limits()

    def test_wizard_date_range_validation(self):
        wiz = self.env['data_seeder.wizard'].create(
            self._wizard_vals(
                date_start=fields.Date.today() + timedelta(days=5),
                date_end=fields.Date.today(),
            )
        )
        with self.assertRaises(ValidationError):
            wiz._check_date_range()

    def test_wizard_percentage_validation(self):
        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals(percent_confirmed=101))
        with self.assertRaises(ValidationError):
            wiz._check_percentages()

        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals(percent_invoiced=-1))
        with self.assertRaises(ValidationError):
            wiz._check_percentages()

        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals(percent_paid=150))
        with self.assertRaises(ValidationError):
            wiz._check_percentages()

        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals(percent_delivered=120))
        with self.assertRaises(ValidationError):
            wiz._check_percentages()

        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals(storable_product_ratio=-10))
        with self.assertRaises(ValidationError):
            wiz._check_percentages()

    def test_wizard_inventory_settings_validation(self):
        wiz = self.env['data_seeder.wizard'].create(
            self._wizard_vals(enable_inventory_flow=True, warehouse_id=False)
        )
        with self.assertRaises(ValidationError):
            wiz._check_inventory_settings()

        wiz = self.env['data_seeder.wizard'].create(
            self._wizard_vals(initial_stock_per_product=-1)
        )
        with self.assertRaises(ValidationError):
            wiz._check_inventory_settings()

    def test_service_generation_smoke(self):
        run = self.env['data_seeder.run'].create({
            'name': 'Automated Test Run',
            'scenario_type': 'sales',
            'state': 'running',
            'start_date': fields.Datetime.now(),
        })

        params = {
            'customer_count': 2,
            'product_count': 2,
            'order_count': 3,
            'avg_lines': 1,
            'percent_confirmed': 100,
            'percent_invoiced': 0,
            'percent_paid': 0,
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today() + timedelta(days=3),
            'min_price': 10.0,
            'max_price': 20.0,
            'min_quantity': 1,
            'max_quantity': 3,
            'company_id': self.env.company.id,
            'run_id': run.id,
        }

        result = self.env['data_seeder.data.generator'].generate(params)

        self.assertEqual(result['customer_count'], 2)
        self.assertEqual(result['product_count'], 2)
        self.assertEqual(result['order_count'], 3)
        self.assertGreaterEqual(result['invoice_count'], 0)
        self.assertGreaterEqual(result['payment_count'], 0)

        run.invalidate_recordset()
        self.assertEqual(len(run.generated_customer_ids), 2)
        self.assertEqual(len(run.generated_product_ids), 2)
        self.assertEqual(len(run.generated_order_ids), 3)

        for product in run.generated_product_ids:
            self.assertGreaterEqual(product.list_price, 10.0)
            self.assertLessEqual(product.list_price, 20.0)

        for order in run.generated_order_ids:
            self.assertGreaterEqual(order.date_order.date(), params['date_start'])
            self.assertLessEqual(order.date_order.date(), params['date_end'])
            for line in order.order_line:
                self.assertGreaterEqual(line.product_uom_qty, 1)
                self.assertLessEqual(line.product_uom_qty, 3)

        self.assertFalse(run.generated_product_ids.filtered('is_storable'))

    def test_service_generation_inventory_aware_products(self):
        run = self.env['data_seeder.run'].create({
            'name': 'Automated Inventory Product Mix Run',
            'scenario_type': 'sales',
            'state': 'running',
            'start_date': fields.Datetime.now(),
        })
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        params = {
            'customer_count': 1,
            'product_count': 6,
            'order_count': 1,
            'avg_lines': 1,
            'percent_confirmed': 0,
            'percent_invoiced': 0,
            'percent_paid': 0,
            'percent_delivered': 0,
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today(),
            'min_price': 10.0,
            'max_price': 20.0,
            'min_quantity': 1,
            'max_quantity': 1,
            'company_id': self.env.company.id,
            'enable_inventory_flow': True,
            'initial_stock_per_product': 7,
            'warehouse_id': warehouse.id,
            'stock_location_id': warehouse.lot_stock_id.id,
            'storable_product_ratio': 50,
            'run_id': run.id,
        }

        result = self.env['data_seeder.data.generator'].generate(params)
        run.invalidate_recordset()

        storable_products = run.generated_product_ids.filtered('is_storable')
        consumable_products = run.generated_product_ids.filtered(lambda product: not product.is_storable)

        self.assertTrue(storable_products)
        self.assertTrue(consumable_products)
        self.assertEqual(len(run.generated_product_ids), 6)
        self.assertEqual(set(result['seeded_product_ids']), set(storable_products.ids))
        self.assertEqual(result['seeded_location_id'], warehouse.lot_stock_id.id)
        self.assertEqual(result['seeded_quantity_total'], len(storable_products) * 7)

        for product in storable_products:
            quantity = self.env['stock.quant']._get_available_quantity(product, warehouse.lot_stock_id)
            self.assertEqual(quantity, 7)

        for product in consumable_products:
            quantity = self.env['stock.quant']._get_available_quantity(product, warehouse.lot_stock_id)
            self.assertEqual(quantity, 0)

    def test_service_tracks_delivery_records(self):
        run = self.env['data_seeder.run'].create({
            'name': 'Automated Delivery Tracking Run',
            'scenario_type': 'sales',
            'state': 'running',
            'start_date': fields.Datetime.now(),
        })
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        params = {
            'customer_count': 2,
            'product_count': 2,
            'order_count': 4,
            'avg_lines': 1,
            'percent_confirmed': 100,
            'percent_invoiced': 0,
            'percent_paid': 0,
            'percent_delivered': 50,
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today(),
            'min_price': 10.0,
            'max_price': 20.0,
            'min_quantity': 1,
            'max_quantity': 1,
            'company_id': self.env.company.id,
            'enable_inventory_flow': True,
            'initial_stock_per_product': 10,
            'warehouse_id': warehouse.id,
            'stock_location_id': warehouse.lot_stock_id.id,
            'storable_product_ratio': 100,
            'run_id': run.id,
        }

        result = self.env['data_seeder.data.generator'].generate(params)
        run.invalidate_recordset()

        self.assertEqual(len(run.generated_picking_ids), 4)
        self.assertEqual(len(run.generated_move_ids), 4)
        self.assertTrue(run.generated_move_line_ids)
        self.assertEqual(result['delivered_count'], 2)
        self.assertEqual(len(run.generated_picking_ids.filtered(lambda picking: picking.state == 'done')), 2)
        self.assertEqual(set(result['picking_ids']), set(run.generated_picking_ids.ids))
        self.assertEqual(set(result['move_ids']), set(run.generated_move_ids.ids))
        self.assertEqual(set(result['move_line_ids']), set(run.generated_move_line_ids.ids))

    def test_cleanup_blocks_done_inventory_pickings(self):
        run = self.env['data_seeder.run'].create({
            'name': 'Automated Inventory Cleanup Guard Run',
            'scenario_type': 'sales',
            'state': 'running',
            'start_date': fields.Datetime.now(),
        })
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        params = {
            'customer_count': 1,
            'product_count': 1,
            'order_count': 1,
            'avg_lines': 1,
            'percent_confirmed': 100,
            'percent_invoiced': 0,
            'percent_paid': 0,
            'percent_delivered': 100,
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today(),
            'min_price': 10.0,
            'max_price': 20.0,
            'min_quantity': 1,
            'max_quantity': 1,
            'company_id': self.env.company.id,
            'enable_inventory_flow': True,
            'initial_stock_per_product': 5,
            'warehouse_id': warehouse.id,
            'stock_location_id': warehouse.lot_stock_id.id,
            'storable_product_ratio': 100,
            'run_id': run.id,
        }

        self.env['data_seeder.data.generator'].generate(params)
        run.invalidate_recordset()

        with self.assertRaises(ValidationError):
            self.env['data_seeder.run.manager'].cleanup_run(run.id, delete_generated_records=True)

    def test_clear_generated_inventory_resets_quants(self):
        run = self.env['data_seeder.run'].create({
            'name': 'Automated Inventory Clear Run',
            'scenario_type': 'sales',
            'state': 'running',
            'start_date': fields.Datetime.now(),
        })
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id),
        ], limit=1)

        params = {
            'customer_count': 1,
            'product_count': 2,
            'order_count': 0,
            'avg_lines': 1,
            'percent_confirmed': 0,
            'percent_invoiced': 0,
            'percent_paid': 0,
            'percent_delivered': 0,
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today(),
            'min_price': 10.0,
            'max_price': 20.0,
            'min_quantity': 1,
            'max_quantity': 1,
            'company_id': self.env.company.id,
            'enable_inventory_flow': True,
            'initial_stock_per_product': 4,
            'warehouse_id': warehouse.id,
            'stock_location_id': warehouse.lot_stock_id.id,
            'storable_product_ratio': 100,
            'run_id': run.id,
        }

        self.env['data_seeder.data.generator'].generate(params)
        run.invalidate_recordset()
        storable_products = run.generated_product_ids.filtered('is_storable')

        self.assertTrue(storable_products)
        self.env['data_seeder.run.manager']._clear_generated_inventory(storable_products)

        for product in storable_products:
            quantity = self.env['stock.quant']._get_available_quantity(product, warehouse.lot_stock_id)
            self.assertEqual(quantity, 0)

    def test_wizard_action_start_generation(self):
        wiz = self.env['data_seeder.wizard'].create(self._wizard_vals())

        action = wiz.action_start_generation()
        wiz.invalidate_recordset()

        self.assertEqual(wiz.state, 'done')
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'data_seeder.run')

        run = self.env['data_seeder.run'].browse(action['res_id'])
        self.assertTrue(run.exists())
        self.assertEqual(run.state, 'done')
        self.assertEqual(run.customer_count, 2)
        self.assertEqual(run.product_count, 2)
        self.assertEqual(run.order_count, 3)
        self.assertFalse(run.generated_picking_ids)
        self.assertFalse(run.generated_move_ids)
        self.assertFalse(run.generated_move_line_ids)

    def test_service_tracks_invoice_and_payment_records(self):
        run = self.env['data_seeder.run'].create({
            'name': 'Automated Accounting Tracking Run',
            'scenario_type': 'sales',
            'state': 'running',
            'start_date': fields.Datetime.now(),
        })

        params = {
            'customer_count': 1,
            'product_count': 1,
            'order_count': 1,
            'avg_lines': 1,
            'percent_confirmed': 100,
            'percent_invoiced': 100,
            'percent_paid': 100,
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today(),
            'min_price': 10.0,
            'max_price': 20.0,
            'min_quantity': 1,
            'max_quantity': 1,
            'company_id': self.env.company.id,
            'run_id': run.id,
        }

        result = self.env['data_seeder.data.generator'].generate(params)
        run.invalidate_recordset()

        self.assertEqual(result['invoice_count'], len(result['invoice_ids']))
        self.assertEqual(result['payment_count'], len(result['payment_ids']))
        self.assertEqual(len(run.generated_invoice_ids), result['invoice_count'])
        self.assertEqual(len(run.generated_payment_ids), result['payment_count'])
        self.assertTrue(run.generated_invoice_ids)
        self.assertTrue(run.generated_payment_ids)
