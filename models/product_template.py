from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    type_pricelist = fields.Selection([
        ('amount', _('Berdasarkan Jumlah')),
        ('one_', _('Satu Harga')),
        ('uom_price', _('Berdasarkan Satuan'))], string='Tipe Harga Jual', default='one_', required=True)
    total_one_ = fields.Float('Satu Harga', related='list_price')
    percent_one_ = fields.Float(string='Persen', )
    
    amount_ids = fields.One2many('product.template.amount', 'product_tmpl_id', string="Harga Jual Berdasarkan Jumlah")
    uom_price_ids = fields.One2many('product.template.uom', 'product_tmpl_id', string="Harga Jual Berdasarkan Satuan")

    @api.multi
    @api.depends('total_one_')
    @api.onchange('total_one_')
    def _one_price_from_one_price(self):
        if self.standard_price:
            self.percent_one_ = ((self.total_one_/self.standard_price) - 1) * 100

    @api.multi
    @api.onchange('percent_one_')
    def _one_price_from_percent(self):
        self.total_one_ = self.standard_price + (self.standard_price*self.percent_one_)/100

class ProductTemplateAmount(models.Model):
    _name = 'product.template.amount'

    product_tmpl_id = fields.Many2one('product.template', string="Product Template")
    amount_from = fields.Integer('Jumlah Minimum')
    amount_to = fields.Integer('Jumlah Maksimum')
    price = fields.Float('Harga')


class ProductTemplateUomPrice(models.Model):
    _name = 'product.template.uom'

    product_tmpl_id = fields.Many2one('product.template', string="Product")
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    price = fields.Float('Harga', required=True, default=0)


