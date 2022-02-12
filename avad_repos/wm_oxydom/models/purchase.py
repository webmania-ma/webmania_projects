# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    controle_workflow = fields.Boolean(string="Controle Workflow", default=False)
    current_rate = fields.Float('Taux actuel', digits=(12, 4), related='currency_id.rate')
    manual_currency_rate_active = fields.Boolean('Appliquer Taux Change Manuel', default=False)
    manual_currency_rate = fields.Float('Taux Change', digits=(12, 4))
    check_shipped = fields.Boolean(compute="_compute_check_shipped")
    currency_name = fields.Char('Currency Name')

    @api.multi
    def call_wizard(self):
        active_id = self._context.get('active_id', False)
        if active_id:
          purchase_obj = self.env['purchase.order'].search([('id', '=', active_id)])
          diff = purchase_obj.currency_id - purchase_obj.company_id.currency_id
          if not diff.id:
              return True
        wizard_form = self.env.ref('wm_oxydom.update_exchange_rate', False)
        return {
            'name': _('Exchnage Rate Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'update.rate',
            'view_id': wizard_form.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }
    def check_exchange_rate(self, value):
        if not value:
            raise ValidationError(_("Taux de change obligatoire"))

    @api.multi
    def action_view_invoice(self):
        for el in self:
            diff = el.currency_id - el.company_id.currency_id
            if diff.id:
                self.check_exchange_rate(el.manual_currency_rate_active)
        res = super(PurchaseOrder, self).action_view_invoice()
        return res

    @api.multi
    def action_view_picking(self):
        for el in self:
            diff = el.currency_id - el.company_id.currency_id
            if diff.id:
              self.check_exchange_rate(el.manual_currency_rate_active)
        res = super(PurchaseOrder, self).action_view_picking()
        return res

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_check_shipped(self):
        for order in self:
            if order.picking_ids and all([x.state == 'done' for x in order.picking_ids]):
                order.check_shipped = True

    @api.multi
    def button_confirm(self):
        self.currency_name = self.currency_id.name
        print(self.currency_name)
        diff = self.currency_id - self.company_id.currency_id
        if self.manual_currency_rate_active and diff.id:
            self = self.with_context(override_currency_rate=self.manual_currency_rate)
        result = super(PurchaseOrder, self).button_confirm()
        return result

    @api.multi
    def button_approve(self, force=False):
        diff = self.currency_id - self.company_id.currency_id
        if self.manual_currency_rate_active and diff.id:
            self = self.with_context(override_currency_rate=self.manual_currency_rate)
        result = super(PurchaseOrder, self).button_approve(force=force)
        return result

    def get_dossier_import(self):
        self.ensure_one()
        picking_ids = self.picking_ids.ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dossier Import',
            'view_mode': 'tree,form',
            'domain': [('picking_ids', 'in', (self.picking_ids.ids))],
            'res_model': 'stock.landed.cost',
            # 'context': "{'create': False}",
            'context': "{'default_picking_ids': %s }" % str(picking_ids)
        }


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    cost_price = fields.Float(string='Prix de revient', related="product_id.product_tmpl_id.standard_price",
                              readonly=True)



    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        diff = self.order_id.currency_id - self.order_id.company_id.currency_id
        if self.order_id.manual_currency_rate_active and diff.id:
            self = self.with_context(override_currency_rate=self.order_id.manual_currency_rate)
        result = super(PurchaseOrderLine, self)._onchange_quantity()
        return result


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if self.purchase_id:
            invoice = self.env['account.invoice']
            self.manual_currency_rate_active = self.purchase_id.manual_currency_rate_active
            self.manual_currency_rate = self.purchase_id.manual_currency_rate
        result = super(AccountInvoice, self).purchase_order_change()
        return result
