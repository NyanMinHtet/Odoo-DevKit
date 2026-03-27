# -*- coding: utf-8 -*-

from odoo import models
from datetime import datetime
import random
import logging

_logger = logging.getLogger(__name__)


class DataSeederWorkflowExecutor(models.AbstractModel):
    _name = 'data_seeder.workflow.executor'
    _description = 'Data Seeder Workflow Executor Service'

    def _execute_workflow(self, order_ids, percent_confirmed=80, percent_invoiced=70,
                          percent_paid=60, percent_delivered=0):
        """Execute sales workflow: confirm orders, process deliveries, invoice, and pay."""
        result = {
            'confirmed_count': 0,
            'delivered_count': 0,
            'invoice_count': 0,
            'payment_count': 0,
            'picking_ids': [],
            'move_ids': [],
            'move_line_ids': [],
            'invoice_ids': [],
            'payment_ids': [],
        }

        # Step 1: Confirm orders
        confirmed_orders = self._confirm_orders(order_ids, percent_confirmed)
        result['confirmed_count'] = len(confirmed_orders)

        # Step 2: Process deliveries
        delivery_result = self._process_deliveries(confirmed_orders, percent_delivered)
        result['delivered_count'] = delivery_result.get('delivered_count', 0)
        result['picking_ids'] = delivery_result.get('picking_ids', [])
        result['move_ids'] = delivery_result.get('move_ids', [])
        result['move_line_ids'] = delivery_result.get('move_line_ids', [])

        # Step 3: Create invoices
        invoiced_orders = self._create_invoices(confirmed_orders, percent_invoiced)
        result['invoice_ids'] = invoiced_orders
        result['invoice_count'] = len(invoiced_orders)

        # Step 4: Register payments
        payments = self._register_payments(invoiced_orders, percent_paid)
        result['payment_ids'] = payments
        result['payment_count'] = len(payments)

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

    def _process_deliveries(self, confirmed_order_ids, percent_delivered):
        """Reserve and validate a percentage of deliveries created from confirmed orders."""
        result = {
            'delivered_count': 0,
            'picking_ids': [],
            'move_ids': [],
            'move_line_ids': [],
        }
        if not confirmed_order_ids:
            return result

        pickings = self._collect_pickings_from_orders(confirmed_order_ids)
        if not pickings:
            return result

        self._assign_pickings(pickings)
        eligible_pickings = pickings.filtered(
            lambda picking: picking.state in ('confirmed', 'assigned', 'partially_available')
        )
        num_to_deliver = int(len(eligible_pickings) * percent_delivered / 100)
        pickings_to_deliver = self.env['stock.picking'].browse(
            random.sample(eligible_pickings.ids, min(num_to_deliver, len(eligible_pickings)))
        )
        delivered_pickings = self._validate_pickings(pickings_to_deliver)

        result['delivered_count'] = len(delivered_pickings)
        result['picking_ids'] = pickings.ids
        result['move_ids'] = pickings.move_ids.ids
        result['move_line_ids'] = pickings.move_line_ids.ids
        return result

    def _collect_pickings_from_orders(self, confirmed_order_ids):
        """Collect stock pickings generated from confirmed sale orders."""
        orders = self.env['sale.order'].browse(confirmed_order_ids).exists()
        pickings = orders.mapped('picking_ids').filtered(lambda picking: picking.state != 'cancel')
        if pickings:
            _logger.info("Collected %s delivery pickings from confirmed orders", len(pickings))
        return pickings

    def _assign_pickings(self, pickings):
        """Reserve stock for eligible pickings."""
        pickings_to_assign = pickings.filtered(
            lambda picking: picking.state in ('confirmed', 'waiting', 'partially_available')
        )
        for picking in pickings_to_assign:
            try:
                picking.action_assign()
            except Exception:
                _logger.exception("Failed to reserve stock for picking %s", picking.name)
        return pickings

    def _validate_pickings(self, pickings):
        """Validate pickings by filling done quantities through the standard stock flow."""
        delivered_pickings = self.env['stock.picking']
        for picking in pickings:
            if picking.state not in ('assigned', 'partially_available', 'confirmed'):
                continue
            if picking.state in ('confirmed', 'partially_available'):
                self._assign_pickings(picking)

            moves_to_process = picking.move_ids.filtered(lambda move: move.state not in ('done', 'cancel'))
            if not moves_to_process:
                continue

            for move in moves_to_process:
                move.quantity = move.product_uom_qty
            moves_to_process.picked = True
            picking.with_context(skip_backorder=True).button_validate()
            if picking.state == 'done':
                delivered_pickings |= picking

        if delivered_pickings:
            _logger.info("Validated %s delivery pickings", len(delivered_pickings))
        return delivered_pickings

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

        payment_ids = []
        for invoice_id in invoices_to_pay:
            invoice = self.env['account.move'].browse(invoice_id)
            if invoice.payment_state == 'not_paid':
                payment_register = self.env['account.payment.register'].with_context({
                    'active_model': 'account.move',
                    'active_ids': [invoice_id],
                }).create({
                    'payment_date': datetime.now().date(),
                    'amount': invoice.amount_residual,
                })
                payments = payment_register._create_payments()
                payment_ids.extend(payments.ids)

        _logger.info(f"Registered {len(payment_ids)} payments")

        return payment_ids
