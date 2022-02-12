# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'
    
    nom = fields.Char('Nom', related='analytic_account_id.name', store=True)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    lot_formatted_export = fields.Char(
        string='Formatted Note',
        compute='_compute_line_lots_export',
        store=True
    )

    @api.multi
    @api.depends('prod_lot_ids')
    def _compute_line_lots_export(self):
        for line in self:
            if line.prod_lot_ids:
                note = u''
                note += u' '.join([
                    u'S/N {0}'.format(lot.name)
                    for lot in line.prod_lot_ids
                ])
                line.lot_formatted_export = note
    


