
{
    "name": "OXYDOM Coût Logistique ",
    "version": "10.0.1.0.0",
    "author": "Webmania",
    "website": "https://www.webmania.ma",
    "category": "Financial Management/Configuration",
    "depends": [
        "base", "purchase", "account", "stock_landed_costs", "stock"
    ],
    "data": [
        "reports/report_bon_commande.xml",
        "reports/report_bon_commande_template.xml",
        "wizard/update_exchange_rate_wizard.xml",
        "views/purchase_view.xml",
        "views/customer_invoice.xml",
    ],
    "installable": True
}
