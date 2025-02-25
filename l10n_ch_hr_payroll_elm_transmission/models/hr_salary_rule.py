from odoo import fields, models


class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _inherit = ['hr.salary.rule', 'mail.thread']

    l10n_ch_code = fields.Char(tracking=True)
    l10n_ch_ac_included = fields.Boolean(tracking=True)
    l10n_ch_aanp_included = fields.Boolean(tracking=True)
    l10n_ch_ijm_included = fields.Boolean(tracking=True)
    l10n_ch_source_tax_included = fields.Boolean(tracking=True)
    l10n_ch_wage_statement = fields.Selection(string="Monthly Statistic",
        selection=[
            ('I', 'I'),
            ('J', 'J'),
            ('K', 'K'),
            ('Y', 'Y'),
            ('L', 'L'),
            ('M', 'M')], tracking=True)
    l10n_ch_yearly_statement = fields.Selection(
        string="Yearly Statistic",
        selection=[
            ('P', 'P'),
            ('O', 'O'),
            ('Q', 'Q'),
            ('R', 'R'),
            ('S', 'S'),
            ('T', 'T')], tracking=True)

    l10n_ch_13th_month_included = fields.Boolean(tracking=True)
    l10n_ch_13th_month_hourly_included = fields.Boolean(tracking=True)
    l10n_ch_vacation_pay_included = fields.Boolean(tracking=True)

    l10n_ch_5_cents_rounding = fields.Boolean(tracking=True)
    l10n_ch_gross_included = fields.Boolean(tracking=True)
    l10n_ch_laac_included = fields.Boolean(tracking=True)
    l10n_ch_lpp_forecast = fields.Boolean(tracking=True)
    l10n_ch_lpp_factor = fields.Integer(tracking=True)
    l10n_ch_lpp_retroactive = fields.Boolean(tracking=True)
    l10n_ch_salary_certificate = fields.Selection(selection=[
        ('1', '1. Salary'),
        ('2.1', '2.1 Room and board'),
        ('2.2', '2.2 Personal use of the company car'),
        ('2.3', '2.3 Personal use of the company car'),
        ('3', '3. Irregular Benefits'),
        ('4', '4. Capital Benefits'),
        ('5', '5. Ownership right in accordance with supplement'),
        ('6', '6. Board of directors’ compensation'),
        ('7', '7. Other benefits'),
        ('8', '8. Gross Salary Total / Pension'),
        ('9', '9. Contributions OASI/DI/IC/UI/NBUV'),
        ('10.1', '10.1 Regular contributions'),
        ('10.2', '10.2 Purchasing contribution'),
        ('11', '11. Net salary / Pension'),
        ('12', '12. Withholding tax deduction'),
        ('13.1.1', '13.1.1. Actual expenses - Trip, room and board'),
        ('13.1.2', '13.1.2. Actual expenses - Others'),
        ('13.2.1', '13.2.1. Overall expenses - Representation'),
        ('13.2.2', '13.2.2. Overall expenses - Car'),
        ('13.2.3', '13.2.3. Overall expenses - Other'),
        ('13.3', '13.3. Contributions to further education'),
        ('14', '14. Further fringe benefits'),
    ], tracking=True)
    l10n_ch_caf_statement = fields.Char(tracking=True)
    l10n_ch_is_periodic = fields.Boolean(tracking=True)
