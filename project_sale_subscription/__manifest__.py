# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Sales Subscription',
    'version': '1.0',
    'category': 'Services/sales/subscriptions',
    'summary': 'Project sales subscriptions',
    'description': 'Bridge created to add the number of subscriptions linked to an AA to a project form',
    'depends': ['sale_project', 'sale_subscription'],
    'data': [
        'views/account_analytic_account_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [
        'demo/product_product_demo.xml',
        'demo/project_task_demo.xml',
        'demo/sale_order_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_sale_subscription/static/src/components/project_right_side_panel/**/*',
        ],
    },
    'installable': True,
    'auto_install': True,
    'author': 'Odoo S.A.',
    'license': 'OEEL-1',
}
