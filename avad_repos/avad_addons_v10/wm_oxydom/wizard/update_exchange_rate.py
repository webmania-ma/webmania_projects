
from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import ValidationError


class AssignExchange(models.TransientModel):

    _name = 'update.rate'

    update_rate = fields.Float(string='X-Rate', digits=(12, 3), required=True)
    exemple = fields.Text(string="Exemple", default="Ex: 8.751", readonly=True)


    @api.multi
    def update_exchange_rate(self):
        active_id = self._context.get('active_id', False)
        purchase_obj = self.env["purchase.order"]
        stock_move_obj = self.env['stock.move']
        for el in self:
            new_exchange_rate = el.update_rate
            current_purchase = purchase_obj.search([('id', '=', active_id)], limit=1)
            if not float_is_zero(new_exchange_rate, precision_digits=1):
                if not current_purchase.manual_currency_rate_active:
                    current_purchase.manual_currency_rate_active=True
                current_purchase.write({'manual_currency_rate': new_exchange_rate, 'manual_currency_rate_active': True})
                for po_line in current_purchase.order_line:
                     source_origin = current_purchase.name
                     if(source_origin):
                        res = self._get_stock_move_price_unit(po_line, new_exchange_rate)
                        product_id = res.get('product_id')
                        price_unit = res.get('proce_unit')
                        stock_move = stock_move_obj.search([('origin', '=', source_origin), ('product_id', '=', product_id)])
                        stock_move.write({'price_unit':price_unit })
            else:
                raise ValidationError(_('Veuillez entrer le X-Rate  superieure ou egal 1'))











    @api.multi
    def _get_stock_move_price_unit(self, line, rate):
        order = line.order_id
        price_unit = line.price_unit
        if line.taxes_id:
            price_unit = line.taxes_id.with_context(round=False).compute_all(
                price_unit, currency=line.order_id.currency_id, quantity=1.0, product=line.product_id,
                partner=line.order_id.partner_id
            )['total_excluded']
        if line.product_uom.id != line.product_id.uom_id.id:
            price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            price_unit = order.currency_id.compute(price_unit, order.company_id.currency_id, round=False)
        return {
            'proce_unit' : price_unit,
            'product_id': line.product_id.id
        }
