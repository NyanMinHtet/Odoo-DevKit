# -*- coding: utf-8 -*-

from odoo import _, models
from odoo.exceptions import ValidationError


class DataSeederInventorySeedService(models.AbstractModel):
    _name = 'data_seeder.inventory.seed.service'
    _description = 'Data Seeder Inventory Seed Service'

    def seed_products(self, product_ids, quantity_per_product=0, company_id=None,
                      warehouse_id=None, location_id=None, log=None):
        """Seed on-hand stock for generated storable products."""
        log = log or []
        quantity_per_product = quantity_per_product or 0
        products = self.env['product.product'].browse(product_ids).exists()
        storable_products = products.filtered('is_storable')

        if not storable_products:
            log.append("Inventory seeding skipped: no tracked goods generated.")
            return {
                'seeded_product_ids': [],
                'seeded_location_id': False,
                'seeded_quantity_total': 0,
            }

        if quantity_per_product <= 0:
            log.append("Inventory seeding skipped: initial stock per product is zero.")
            return {
                'seeded_product_ids': storable_products.ids,
                'seeded_location_id': False,
                'seeded_quantity_total': 0,
            }

        company = self.env['res.company'].browse(company_id).exists() or self.env.company
        location = self._resolve_stock_location(
            company=company,
            warehouse_id=warehouse_id,
            location_id=location_id,
        )

        quant_model = self.env['stock.quant'].with_company(company)
        for product in storable_products:
            quant_model._update_available_quantity(product, location, quantity_per_product)

        seeded_total = quantity_per_product * len(storable_products)
        log.append(
            "Seeded %s units across %s tracked goods in %s."
            % (seeded_total, len(storable_products), location.display_name)
        )

        return {
            'seeded_product_ids': storable_products.ids,
            'seeded_location_id': location.id,
            'seeded_quantity_total': seeded_total,
        }

    def _resolve_stock_location(self, company, warehouse_id=None, location_id=None):
        """Resolve an internal stock location suitable for inventory seeding."""
        if location_id:
            location = self.env['stock.location'].browse(location_id).exists()
            if not location:
                raise ValidationError(_("The selected stock location does not exist."))
            if location.usage != 'internal':
                raise ValidationError(_("Inventory seeding requires an internal stock location."))
            if location.company_id and location.company_id != company:
                raise ValidationError(_("The selected stock location must belong to the chosen company."))
            return location

        if warehouse_id:
            warehouse = self.env['stock.warehouse'].browse(warehouse_id).exists()
            if not warehouse:
                raise ValidationError(_("The selected warehouse does not exist."))
            if warehouse.company_id and warehouse.company_id != company:
                raise ValidationError(_("The selected warehouse must belong to the chosen company."))
            if warehouse.lot_stock_id:
                return warehouse.lot_stock_id

        location = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            '|', ('company_id', '=', False), ('company_id', '=', company.id),
        ], limit=1)
        if not location:
            raise ValidationError(_("No internal stock location is available for the selected company."))
        return location
