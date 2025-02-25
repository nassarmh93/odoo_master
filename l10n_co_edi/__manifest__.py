# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Electronic invoicing for Colombia with Carvajal',
    'version': '0.3',
    'category': 'Accounting/Localizations/EDI',
    'summary': 'Colombian Localization for EDI documents',
    'author': 'Odoo Sa',
    'depends': ['account_edi', 'l10n_co', 'product_unspsc', 'base_address_extended'],
    'auto_install': ['l10n_co'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_edi_data.xml',
        'data/l10n_co_edi.type_code.csv',
        'data/l10n_co_edi.tax.type.csv',
        'data/l10n_co_edi.payment.option.csv',
        'data/res_partner_data.xml',
        'data/res.city.csv',
        'data/res.country.state.csv',
        'data/res_country_data.xml',
        'views/res_company_views.xml',
        'views/account_invoice_views.xml',
        'views/account_tax_views.xml',
        'views/account_journal_views.xml',
        'views/product_template_views.xml',
        'views/product_uom_views.xml',
        'views/type_code_views.xml',
        'views/res_partner_views.xml',
        'views/tax_type_views.xml',
        'views/res_config_settings_views.xml',
        'views/electronic_invoice.xml',
        'views/electronic_invoice_vendor_document.xml',
        'views/portal_address_templates.xml',
        'wizards/account_move_reversal_view.xml',
        'wizards/account_debit_note_view.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'l10n_co_edi/static/src/js/portal_address.js',
        ],
    },
    'installable': True,
    'license': 'OEEL-1',
    'post_init_hook': '_l10n_co_edi_post_init',
}
