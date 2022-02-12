
from odoo import fields, models, api

class LandedCostInherit(models.Model):
    _inherit = 'stock.landed.cost'

    @api.multi
    def button_validate(self):
        res = super(LandedCostInherit, self).button_validate()
        purchase_order_obj = self.env['purchase.order'].search([('name', '=', self.picking_ids[0].origin)])
        diff = purchase_order_obj.currency_id - purchase_order_obj.company_id.currency_id
        if  diff.id:
            for cost in self:
                for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                    quants = line.move_id.quant_ids.sorted(key=lambda r: r.qty, reverse=True)
                    for quant in quants:
                        quant_cost = quant.cost
                        product_id = quant.product_id.product_tmpl_id.id
                        for line in purchase_order_obj.order_line:
                            if line.product_id.product_tmpl_id.id == product_id:
                                #standard_price = quant_cost / line.product_qty
                                standard_price = quant_cost
                                product_tpl = self.env['product.template'].search(
                                    [('id', '=', line.product_id.product_tmpl_id.id)])
                                product_tpl.write({'standard_price': standard_price})
        return res
