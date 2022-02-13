# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.addons.base.res.res_currency import Currency

class CurrencyExt(models.Model):
    _inherit = 'res.currency'

    @api.model_cr
    def _register_hook(self):
        @api.model
        def _get_conversion_rate_enhanced(self, from_currency, to_currency):
            id = self._context.get('default_purchase_id') or self._context.get('active_id')
            purchase_id = self.env['purchase.order'].search([('id', '=',id )])
            manual_rate = self._context.get('override_currency_rate', False)
            if not manual_rate:
                if purchase_id.manual_currency_rate_active:
                    manual_rate = purchase_id.manual_currency_rate
            from_invoice = self._context.get('from_invoice', False)
            from_currency = from_currency.with_env(self.env)
            to_currency = to_currency.with_env(self.env)
            if (from_invoice):
                return manual_rate
            if not manual_rate:
                return to_currency.rate / from_currency.rate
            else:
                return to_currency.rate / manual_rate

        Currency._get_conversion_rate = _get_conversion_rate_enhanced
        return super(CurrencyExt, self)._register_hook()