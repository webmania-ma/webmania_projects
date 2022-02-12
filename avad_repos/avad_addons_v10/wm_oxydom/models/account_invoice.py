# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.invoice_id.manual_currency_rate_active:
            self = self.with_context(override_currency_rate=self.invoice_id.manual_currency_rate)
        return super(AccountInvoiceLine, self)._onchange_product_id()


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    manual_currency_rate_active = fields.Boolean('Appliquer Taux Change Manuel')
    manual_currency_rate = fields.Float('Taux Change', digits=(12, 4))
    last_currency = fields.Float('Last Rate', digits=(12, 4))

    @api.multi
    def action_move_create(self):
        if self.manual_currency_rate_active:
            self = self.with_context(override_currency_rate=self.manual_currency_rate)
        return super(AccountInvoice, self).action_move_create()

    def _compute_price_2(self):
        for elem in self.invoice_line_ids:
            currency = elem.invoice_id and elem.invoice_id.currency_id or None
            price = elem.price_unit * (1 - (elem.discount or 0.0) / 100.0)
            if (elem.invoice_id.last_currency == 0.0):
                price_ori_line = elem.invoice_id.company_id.currency_id.with_context(from_invoice=True).compute(price,
                                                                                                                elem.partner_id.property_purchase_currency_id)
            else:
                price_ori_line = elem.invoice_id.company_id.currency_id.with_context(from_invoice=True,
                                                                                     override_currency_rate=elem.invoice_id.last_currency).compute(
                    price, elem.partner_id.property_purchase_currency_id)
            converted_price = elem.invoice_id.partner_id.property_purchase_currency_id.with_context(
                override_currency_rate=elem.invoice_id.manual_currency_rate).compute(price_ori_line,
                                                                                     elem.company_id.currency_id)
            elem.price_unit = converted_price
            elem.invoice_id.last_currency = elem.invoice_id.manual_currency_rate

    @api.multi
    def recalculate(self):
        for inv in self:
            if inv.currency_id.id == inv.company_id.currency_id.id and inv.manual_currency_rate_active:
                inv._compute_price_2()
            else:
                raise ValidationError(
                    _('Please Switch Invoice Currency to your Company Currency (%s)' % inv.company_id.currency_id.name))
