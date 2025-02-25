# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from . import models


def _l10n_cz_reports_post_init(env):
    for company in env['res.company'].search([('chart_template', '=', 'cz')], order="parent_path"):
        Template = env['account.chart.template'].with_company(company)
        Template._load_data({
            'account.tax': Template._get_cz_control_statement_account_tax(),
        })
