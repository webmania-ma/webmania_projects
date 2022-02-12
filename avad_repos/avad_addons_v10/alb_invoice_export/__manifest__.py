# -*- coding: utf-8 -*-
{
    'name': "alb_invoice_export",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_payment_partner', 'avad_base', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_export_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}