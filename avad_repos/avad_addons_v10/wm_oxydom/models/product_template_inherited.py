from odoo import fields, models, api, _
from odoo.exceptions import ValidationError



class PurchaseOrder(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):

        defaultcode = vals.get('default_code')
        output = self.env['product.template'].search([('default_code', '=', defaultcode)])
        if len(output.ids) > 0:
            raise ValidationError(_("Internal reference must be unique"))
        result = super(PurchaseOrder, self).create(vals)
        return result


