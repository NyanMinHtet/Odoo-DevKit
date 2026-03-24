# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.tools import config
from datetime import datetime, timedelta
import random
import logging
import faker

_logger = logging.getLogger(__name__)

try:
    from faker import Faker
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False
    _logger.warning("Faker library not installed. Install with: pip install faker")
    Faker = None  # type: ignore


class DataSeederDataGenerator(models.AbstractModel):
    _name = 'data_seeder.data.generator'
    _description = 'Data Seeder Data Generator Service'

    def generate(self, params):
        """Main generation entry point"""
        start_time = datetime.now()
        log = []
        result = {
            'customer_count': 0,
            'product_count': 0,
            'order_count': 0,
            'invoice_count': 0,
            'payment_count': 0,
            'execution_time': 0,
            'log': '',
        }

        # Initialize Faker
        fake = Faker() if HAS_FAKER else None

        # Get company
        company = self.env['res.company'].browse(params.get('company_id'))
        if not company.exists():
            company = self.env.company

        log.append(f"Starting generation at {datetime.now()}")
        log.append(f"Configuration: {params}")

        # Step 1: Generate Customers
        customer_ids = self._generate_customers(
            count=params.get('customer_count', 10),
            fake=fake,
            company=company,
        )
        result['customer_count'] = len(customer_ids)
        log.append(f"Created {result['customer_count']} customers")

        # Step 2: Generate Products
        product_ids = self._generate_products(
            count=params.get('product_count', 5),
            fake=fake,
            min_price=params.get('min_price', 10.0),
            max_price=params.get('max_price', 500.0),
            company=company,
        )
        result['product_count'] = len(product_ids)
        log.append(f"Created {result['product_count']} products")

        # Step 3: Generate Sale Orders
        order_ids = self._generate_sale_orders(
            count=params.get('order_count', 20),
            customer_ids=customer_ids,
            product_ids=product_ids,
            avg_lines=params.get('avg_lines', 3),
            min_qty=params.get('min_quantity', 1),
            max_qty=params.get('max_quantity', 50),
            date_start=params.get('date_start'),
            date_end=params.get('date_end'),
            company=company,
        )
        result['order_count'] = len(order_ids)
        log.append(f"Created {result['order_count']} sale orders")

        # Step 4: Execute Workflow
        workflow_result = self.env['data_seeder.workflow.executor']._execute_workflow(
            order_ids=order_ids,
            percent_confirmed=params.get('percent_confirmed', 80),
            percent_invoiced=params.get('percent_invoiced', 70),
            percent_paid=params.get('percent_paid', 60),
        )
        result['invoice_count'] = workflow_result.get('invoice_count', 0)
        result['payment_count'] = workflow_result.get('payment_count', 0)
        log.append(f"Confirmed {workflow_result.get('confirmed_count', 0)} orders")
        log.append(f"Created {result['invoice_count']} invoices")
        log.append(f"Registered {result['payment_count']} payments")

        # Update run record if provided
        if params.get('run_id'):
            run = self.env['data_seeder.run'].browse(params['run_id'])
            if run.exists():
                run.write({
                    'generated_customer_ids': [(6, 0, customer_ids)],
                    'generated_product_ids': [(6, 0, product_ids)],
                    'generated_order_ids': [(6, 0, order_ids)],
                })

        end_time = datetime.now()
        result['execution_time'] = (end_time - start_time).total_seconds()
        result['log'] = '\n'.join(log)

        _logger.info(f"Generation completed in {result['execution_time']:.2f}s")
        return result

    def _generate_customers(self, count, fake=None, company=None):
        """Generate customer records"""
        customer_ids = []
        customers = []

        for i in range(count):
            if fake:
                name = fake.company() if random.random() > 0.3 else fake.name()
                email = fake.email()
                phone = fake.phone_number()
                street = fake.street_address()
                city = fake.city()
                zip_code = fake.postcode()
            else:
                name = f"Test Customer {i+1}"
                email = f"customer{i+1}@test.com"
                phone = f"+12345678{i:02d}"
                street = f"Test Street {i+1}"
                city = "Test City"
                zip_code = f"00{i:02d}"

            customers.append({
                'name': name,
                'email': email,
                'phone': phone,
                'street': street,
                'street2': '',
                'city': city,
                'zip': zip_code,
                'country_id': self.env['res.country'].search([], limit=1).id,
                'is_company': random.choice([True, False]),
                'company_id': company.id if company else False,
            })

        # Create customers in batch
        created = self.env['res.partner'].create(customers)
        customer_ids = created.ids

        return customer_ids

    def _generate_products(self, count, fake=None, min_price=10.0, max_price=500.0, company=None):
        """Generate product records"""
        product_ids = []
        products = []
        categ = self.env['product.category'].search([], limit=1)

        for i in range(count):
            if fake:
                name = fake.catch_phrase()
            else:
                name = f"Test Product {i+1}"

            price = random.uniform(min_price, max_price)
            products.append({
                'name': name,
                'list_price': price,
                'standard_price': price * 0.6,
                'categ_id': categ.id,
                'type': 'consu',
                'company_id': company.id if company else False,
            })

        created = self.env['product.product'].create(products)
        product_ids = created.ids

        return product_ids

    def _generate_sale_orders(self, count, customer_ids, product_ids, avg_lines=3,
                              min_qty=1, max_qty=50, date_start=None, date_end=None, company=None):
        """Generate sale order records"""
        order_ids = []

        if not customer_ids or not product_ids:
            return []

        date_start = date_start or datetime.now().date()
        date_end = date_end or (datetime.now().date() + timedelta(days=30))

        for i in range(count):
            # Random customer
            customer_id = random.choice(customer_ids)
            customer = self.env['res.partner'].browse(customer_id)

            # Random date
            delta_days = (date_end - date_start).days
            random_date = date_start + timedelta(days=random.randint(0, delta_days))

            # Create order
            order = self.env['sale.order'].create({
                'partner_id': customer_id,
                'date_order': random_date,
                'company_id': company.id if company else False,
            })

            # Add order lines
            num_lines = random.randint(1, avg_lines * 2)
            for _ in range(num_lines):
                product_id = random.choice(product_ids)
                product = self.env['product.product'].browse(product_id)
                qty = random.randint(min_qty, max_qty)

                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'product_id': product_id,
                    'product_uom_qty': qty,
                    'product_uom': product.uom_id.id,
                    'price_unit': product.list_price,
                })

            order_ids.append(order.id)

        return order_ids
