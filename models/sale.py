from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self)

        if not self.product_id:
            return {'domain': {'product_uom': []}}

        price_unit = self.price_unit

        self.product_id
        product_tmp = self.env['product.template'].search([
            ('id', '=', self.product_id.id)
        ])
        
        type_pricelist_prod = product_tmp.type_pricelist
        
        if(type_pricelist_prod == 'amount'):
            prod_amount = self.env['product.template.amount'].search([
                ('product_tmpl_id', '=', self.product_id.id),
                ('amount_from', '<=', self.product_uom_qty),
                ('amount_to', '>=', self.product_uom_qty)
            ])
            price_unit = prod_amount.price

        if(type_pricelist_prod == 'one_'):
            price_unit = product_tmp.total_one_

        if(type_pricelist_prod == 'uom_price'):
            prod_uom = self.env['product.template.uom'].search([
                ('product_tmpl_id', '=', self.product_id.id),
                ('uom_id', '=', self.product_uom.id),
            ])
            price_unit = prod_uom.price
        
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale

        res.update({
            'price_unit': price_unit,
            'name': name
        })

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(SaleOrderLine, self)

        price_unit = self.price_unit

        self.product_id
        product_tmp = self.env['product.template'].search([
            ('id', '=', self.product_id.id)
        ])
        
        type_pricelist_prod = product_tmp.type_pricelist
        
        if(type_pricelist_prod == 'amount'):
            prod_amount = self.env['product.template.amount'].search([
                ('product_tmpl_id', '=', self.product_id.id),
                ('amount_from', '<=', self.product_uom_qty),
                ('amount_to', '>=', self.product_uom_qty)
            ])
            price_unit = prod_amount.price

        if(type_pricelist_prod == 'uom_price'):
            prod_uom = self.env['product.template.uom'].search([
                ('product_tmpl_id', '=', self.product_id.id),
                ('uom_id', '=', self.product_uom.id),
            ])
            price_unit = prod_uom.price

        res.update({
            'price_unit': price_unit
        })