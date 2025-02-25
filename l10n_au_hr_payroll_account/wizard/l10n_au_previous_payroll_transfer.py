# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.l10n_au_hr_payroll.models.hr_employee import INCOME_STREAM_TYPES


class L10n_AuPreviousPayrollTransfer(models.TransientModel):
    _name = 'l10n_au.previous.payroll.transfer'
    _description = "Transfer From Previous Payroll System"

    def _default_fiscal_year_start_date(self):
        company = self.env.company
        start_month = int(company.fiscalyear_last_month) + 1 if int(company.fiscalyear_last_month) < 12 else 1
        return fields.Date.today().replace(month=start_month, day=1)

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    previous_bms_id = fields.Char(string="Previous BMS ID", required=True, help="Enter the ID of the employee in the previous payroll system.")
    l10n_au_previous_payroll_transfer_employee_ids = fields.One2many("l10n_au.previous.payroll.transfer.employee", "l10n_au_previous_payroll_transfer_id")
    fiscal_year_start_date = fields.Date(
        string="Fiscal Year Start Date",
        required=True,
        default=_default_fiscal_year_start_date
    )

    def action_transfer(self):
        self.ensure_one()
        if self.company_id.l10n_au_previous_bms_id:
            raise UserError(_("This company already has a previous BMS ID set."))

        self.company_id.write({"l10n_au_previous_bms_id": self.previous_bms_id})
        for rec in self.l10n_au_previous_payroll_transfer_employee_ids:
            rec.employee_id.l10n_au_previous_payroll_id = rec.previous_payroll_id
        prev_pay_transfer_employees = self.l10n_au_previous_payroll_transfer_employee_ids.filtered(lambda x: x.import_ytd)

        return self.company_id._create_ytd_values(prev_pay_transfer_employees, self.fiscal_year_start_date)\
            .with_context(search_default_filter_group_employee_id=1, search_default_filter_group_income_stream= 1)\
            ._get_records_action(name=_("Opening Balances"))


class L10n_AuPreviousPayrollTransferEmployee(models.TransientModel):
    _name = 'l10n_au.previous.payroll.transfer.employee'
    _description = "Employee Transfer From Previous Payroll System"

    l10n_au_previous_payroll_transfer_id = fields.Many2one("l10n_au.previous.payroll.transfer", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="l10n_au_previous_payroll_transfer_id.company_id")
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    previous_payroll_id = fields.Char(
        "Previous Payroll ID",
        compute="_compute_payroll_id", size=20,
        required=True, store=True, readonly=False,
    )
    l10n_au_income_stream_type = fields.Selection(
        selection=INCOME_STREAM_TYPES,
        string="Income Stream Type",
        compute="_compute_income_stream_type",
        required=True, store=True, readonly=False
    )
    import_ytd = fields.Boolean("Import YTD Balances", default=True)

    _unique_employee_transfer = models.Constraint(
        'unique(employee_id, l10n_au_previous_payroll_transfer_id, l10n_au_income_stream_type)',
        "An employee can only be transferred once per Income Stream Type.",
    )

    @api.depends("employee_id")
    def _compute_payroll_id(self):
        for rec in self:
            rec.previous_payroll_id = rec.employee_id.l10n_au_previous_payroll_id

    @api.depends("employee_id")
    def _compute_income_stream_type(self):
        for rec in self:
            rec.l10n_au_income_stream_type = rec.employee_id.l10n_au_income_stream_type
