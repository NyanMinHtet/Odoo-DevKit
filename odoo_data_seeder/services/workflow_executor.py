# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime
import random
import logging

_logger = logging.getLogger(__name__)


class DataSeederWorkflowExecutor(models.AbstractModel):
    _name = 'data_seeder.workflow.executor'
    _description = 'Data Seeder Workflow Executor Service'

    def _execute_workflow(self, order_ids, percent_confirmed=80, percent_invoiced=70, percent_paid=60):
        """Execute sales workflow: confirm orders, create invoices, register payments"""
        result = {
            'confirmed_count': 0,
            'invoice_count': 0,
            'payment_count': 0,
        }

        # Step 1: Confirm orders
        confirmed_orders = self._confirm_orders(order_ids, percent_confirmed)
        result['confirmed_count'] = len(confirmed_orders)

        # Step 2: Create invoices
        invoiced_orders = self._create_invoices(confirmed_orders, percent_invoiced)
        result['invoice_count'] = len(invoiced_orders)

        # Step 3: Register payments
        paid_invoices = self._register_payments(invoiced_orders, percent_paid)
        result['payment_count'] = len(paid_invoices)

        return result

    def _confirm_orders(self, order_ids, percent_confirmed):
        """Confirm a percentage of orders"""
        if not order_ids:
            return []

        num_to_confirm = int(len(order_ids) * percent_confirmed / 100)
        orders_to_confirm = random.sample(order_ids, min(num_to_confirm, len(order_ids)))

        orders = self.env['sale.order'].browse(orders_to_confirm)
        confirmed = orders.filtered(lambda o: o.state == 'draft')

        if confirmed:
            confirmed.action_confirm()
            _logger.info(f"Confirmed {len(confirmed)} sale orders")

        return confirmed.ids

    def _create_invoices(self, confirmed_order_ids, percent_invoiced):
        """Create invoices for confirmed orders"""
        if not confirmed_order_ids:
            return []

        orders = self.env['sale.order'].browse(confirmed_order_ids)
        invoiced_orders = orders.filtered(lambda o: o.invoice_status == 'to invoice')

        num_to_invoice = int(len(invoiced_orders) * percent_invoiced / 100)
        orders_to_invoice = random.sample(invoiced_orders.ids, min(num_to_invoice, len(invoiced_orders)))

        invoices = []
        for order_id in orders_to_invoice:
            order = self.env['sale.order'].browse(order_id)
            if order.invoice_status == 'to invoice':
                # Create down payment invoice (0% down payment = full invoice)
                invoice_ids = order._create_invoices(final=True)
                if invoice_ids:
                    invoices.extend(invoice_ids.ids)

        # Post invoices
        if invoices:
            moves = self.env['account.move'].browse(invoices)
            moves.filtered(lambda m: m.state == 'draft').action_post()
            _logger.info(f"Created and posted {len(invoices)} invoices")

        return invoices

    def _register_payments(self, invoice_ids, percent_paid):
        """Register payments for invoices"""
        if not invoice_ids:
            return []

        invoices = self.env['account.move'].browse(invoice_ids)
        posted_invoices = invoices.filtered(lambda i: i.state == 'posted' and i.payment_state == 'not_paid')

        num_to_pay = int(len(posted_invoices) * percent_paid / 100)
        invoices_to_pay = random.sample(posted_invoices.ids, min(num_to_pay, len(posted_invoices)))

        paid_count = 0
        for invoice_id in invoices_to_pay:
            invoice = self.env['account.move'].browse(invoice_id)
            if invoice.payment_state == 'not_paid':
                # Register payment
                payment_register = self.env['account.payment.register'].with_context({
                    'active_model': 'account.move',
                    'active_ids': [invoice_id],
                }).create({
                    'payment_date': datetime.now().date(),
                    'amount': invoice.amount_residual,
                })
                payment_register.action_create_payments()
                paid_count += 1

        _logger.info(f"Registered {paid_count} payments")

        return list(range(paid_count))  # Return count as list for consistency
