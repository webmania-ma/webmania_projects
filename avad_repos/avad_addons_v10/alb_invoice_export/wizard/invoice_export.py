# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from pprint import pprint
import xlwt
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class InvoiceExportWizard(models.TransientModel):
    _name = 'invoice.export.wizard'

    date_from = fields.Date("De", required=True)
    date_end = fields.Date("A", required=True)
    ouvert = fields.Boolean(u'Ouverte')
    paid = fields.Boolean(u'Payée')
    partial = fields.Boolean(u'Partiellement payée')
    

    def action_print(self):
        data = {}
        query = """
           SELECT
                 partner.id as customer_code,
                 partner.name as customer,
                 medecin.name as medecin,
                 specialite.name as specialite,
                 ai.number as invoice_number,
                 ai.date_invoice AS date,
                 project.demande as projet,
                 agence.name as agence,
                 pr.default_code as product_code,
                 pt.name as product,
                 ail.lot_formatted_export as sn,
                 categ.name as category,
                 ail.quantity as quantity,
                 acc.name as analytic_account,
                 (quantity * ail.price_unit * (1 - ail.discount / 100)) as prix_ht,
                 (ail.price_subtotal * (1 - ail.discount / 100)) as prix_ttc,
                 payment_mode.name as payment_mode,
                 CASE 
                       WHEN ai.state = 'open' and ai.residual = ai.amount_total THEN 'open'
                       WHEN ai.state = 'open' and ai.residual != ai.amount_total THEN 'partial'
                       WHEN ai.state = 'paid' THEN 'paid'
                       ELSE ''
                 END as payment_state   

           FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON partner.id = ai.partner_id
                LEFT JOIN project_project project ON project.id = ai.our_project_id
                LEFT JOIN account_analytic_account prj ON prj.id = project.analytic_account_id
                LEFT JOIN res_partner medecin ON medecin.id = project.medecin_prescripteur_id
                LEFT JOIN avad_medcin_specialite specialite ON specialite.id = medecin.specialite
                LEFT JOIN crm_team agence ON agence.id = ai.agence_id
                LEFT JOIN account_payment_mode payment_mode ON payment_mode.id = ai.payment_mode_id
                left JOIN account_analytic_account acc ON acc.id = ail.account_analytic_id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                left JOIN product_template pt ON pt.id = pr.product_tmpl_id
                left JOIN product_category categ ON categ.id = pt.categ_id
            WHERE
                ai.date_invoice <= %s and ai.date_invoice >= %s and ai.type = 'out_invoice'
                
            
            
                
       
        """
        self._cr.execute(query, (self.date_end,self.date_from))
        ail_data = self._cr.dictfetchall()
        data['invoive_lines'] = ail_data
        states = []
        if self.ouvert:
            states.append('open')
        if self.paid:
            states.append('paid')
        if self.partial:
            states.append('partial')
        data['states'] = states
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'invoice.export.wizard.xlsx',
            'datas': data,
        }


class PartnerXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, partners):
        dict = {
            'open' : u'Ouverte',
            'partial' : u'Partiellement payée',
            'paid' : u'Payée',
        }
        for obj in partners:



            sheet = workbook.add_worksheet("Statistique de vente")

            sheet.set_column(1, 16, 20)
            sheet.set_row(0, 80)
            sheet.set_row(2, 40)
            merge_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'font_size': 25,
                'fg_color': '#276678',
                'font_color': '#FFFFFF',
            })

            sheet.merge_range('D1:G1', u"Statistiques de vente ERP OXYDOM", merge_format)
            sheet.insert_image('A2', 'alb_invoive_export/static/imgs/logo.png')

            header_format = workbook.add_format({
                'font_name': "Arial",
                'bold': True,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'fg_color': '#1687a7',
                'font_color': '#FFFFFF',
            })

            sheet.write(2, 1, u"Code  Patient", header_format)
            sheet.write(2, 2, u"Nom Patient", header_format)
            sheet.write(2, 3, u"Médecin", header_format)
            sheet.write(2, 4, u"Spécialité", header_format)
            sheet.write(2, 5, u"N° Facture", header_format)
            sheet.write(2, 6, u"Date Facture", header_format)
            sheet.write(2, 7, u"Type de besoin", header_format)
            sheet.write(2, 8, u"Agence", header_format)
            sheet.write(2, 9, u"Ligne Facture / Référence Article", header_format)
            sheet.write(2, 10, u"Ligne Facture / Nom Article", header_format)
            sheet.write(2, 11, u"Ligne Facture / SN", header_format)
            sheet.write(2, 12, u"Ligne Facture / Catégorie Article", header_format)
            sheet.write(2, 13, u"Ligne Facture /Compte Comptable", header_format)
            sheet.write(2, 14, u"Ligne Facture /Quantité", header_format)
            sheet.write(2, 15, u"Ligne Facture /Total HT", header_format)
            sheet.write(2, 16, u"Ligne Facture /Total TTC", header_format)
            sheet.write(2, 17, u"Etat de Paiement", header_format)
            sheet.write(2, 18, u"Mode de Paiement", header_format)
            row = 3

            for line in data['invoive_lines']:
                if line['payment_state'] in data['states']:
                    sheet.write(row, 1, line['customer_code'])
                    sheet.write(row, 2, line['customer'])
                    sheet.write(row, 3, line['medecin'])
                    sheet.write(row, 4, line['specialite'])
                    sheet.write(row, 5, line['invoice_number'])
                    sheet.write(row, 6, line['date'])
                    sheet.write(row, 7, line['projet'])
                    sheet.write(row, 8, line['agence'])
                    sheet.write(row, 9, line['product_code'])
                    sheet.write(row, 10, line['product'])
                    sheet.write(row, 11, line['sn'])
                    sheet.write(row, 12, line['category'])
                    sheet.write(row, 13, line['analytic_account'])
                    sheet.write(row, 14, line['quantity'])
                    sheet.write(row, 15, line['prix_ttc'])
                    sheet.write(row, 16, line['prix_ht'])
                    sheet.write(row, 17, dict[line['payment_state']] or '')
                    sheet.write(row, 18, line['payment_mode'])
                    row += 1

PartnerXlsx('report.invoice.export.wizard.xlsx',
            'invoice.export.wizard')
