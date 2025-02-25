# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Egypt - Payroll",
    "countries": ["eg"],
    "category": "Human Resources/Payroll",
    "description": """
Egypt Payroll and End of Service rules.
=======================================

    """,
    "depends": ["hr_payroll"],
    "auto_install": ["hr_payroll"],
    "data": [
        "data/hr_rule_parameter_data.xml",
        "data/hr_salary_rule_category_data.xml",
        "data/hr_payroll_structure_type_data.xml",
        "data/hr_payroll_structure_data.xml",
        "data/hr_salary_rule_data.xml",
        "views/hr_contract_views.xml",
    ],
    "author": "Odoo S.A.",
    "license": "OEEL-1",
    'demo': [
        'data/l10n_eg_hr_payroll_demo.xml',
    ],
}
