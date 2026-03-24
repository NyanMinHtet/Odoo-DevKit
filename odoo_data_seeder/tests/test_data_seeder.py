# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestDataSeeder(TransactionCase):

    def _wizard_vals(self, **overrides):
        today = fields.Date.today()
        vals = {
            'customer_count': 2,
            'product_count': 2,
            'order_count': 3,
            'avg_lines_per_order': 1,
            'percent_confirmed': 100,
            'percent_invoiced': 0,
            'percent_paid': 0,
            'date_start': today,
            'date_end': today + timedelta(days=7),
            'min_price': 10.0,
            'max_price': 20.0,
            'min_quantity': 1,
            'max_quantity': 3,
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
