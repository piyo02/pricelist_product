from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    type_pricelist = fields.Selection([
        ('amount', _('Berdasarkan Jumlah')),
        ('one_', _('Satu Harga')),
        ('uom_price', _('Berdasarkan Satuan'))], string='Pricelist Type', default='amount', required=True )
    percent_one_ = fields.Float(string='Percent')
    total_one_ = fields.Float('One Price', _compute='_one_price')
    
    amount_ids = fields.One2many('product.template.amount', 'product_tmpl_id', string="Pricelist based on Amount")
    uom_price_ids = fields.One2many('product.template.uom', 'product_tmpl_id', string="Pricelist based on uom")

    @api.multi
    @api.onchange('percent_one_')
    def _one_price(self):
        self.total_one_ = self.list_price + (self.list_price*self.percent_one_)/100

class ProductTemplateAmount(models.Model):
    _name = 'product.template.amount'

    product_tmpl_id = fields.Many2one('product.template', string="Product Template")
    amount_from = fields.Integer('Jumlah Minimum')
    amount_to = fields.Integer('Jumlah Maksimum')
    price = fields.Float('Harga')


class ProductTemplateUomPrice(models.Model):
    _name = 'product.template.uom'

    product_tmpl_id = fields.Many2one('product.template', string="Product Template")
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    price = fields.Float('Harga')


