# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date


class HrPayslipEmployees(models.TransientModel):
    _name = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'

    def _get_available_contracts_domain(self):
        payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        domain = ['|',
            ('contract_ids.date_end', '=', False),
            ('contract_ids.date_end', '>', payslip_run.date_start),
            ('contract_ids.state', 'in', ('open', 'close')),
            ('company_id', '=', self.env.company.id),
        ]
        return domain

    def _get_employees(self):
        active_employee_ids = self.env.context.get('active_employee_ids', False)
        if active_employee_ids:
            return self.env['hr.employee'].browse(active_employee_ids)
        # YTI check dates too
        return self.env['hr.employee'].search(self._get_available_contracts_domain())

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
                                    default=lambda self: self._get_employees(), required=True,
                                    compute='_compute_employee_ids', store=True, readonly=False)
    selection_mode = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('job', 'By Job Position'),
        ('structure', 'By Salary Structure Types'),
        ('category', 'By Employee Tags')],
        string='Selection Mode', readonly=False, required=True, default='employee',
        help="Allow to select employees in batchs:\n- By Employee: for a specific employee"
             "\n- By Department: all employees of the specified department"
             "\n- By Job Position: all employees of the specified job position"
             "\n- By Salary Structure Types: all employees of the specified salary structure types"
             "\n- By Employee Tags: all employees of the specific employee group category")
    structure_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', compute='_compute_structure_id', readonly=False, store=True)
    structure_type_ids = fields.Many2many('hr.payroll.structure.type', string='Salary Structure Type')
    job_ids = fields.Many2many('hr.job', string='Job Position')
    department_ids = fields.Many2many('hr.department')
    select_employee_ids = fields.Many2many('hr.employee', string='Select Employees', domain="[('company_id', 'in', allowed_company_ids)]")
    category_ids = fields.Many2many('hr.employee.category', string='Employee Tag')

    @api.depends('structure_id', 'department_ids', 'structure_type_ids', 'job_ids', 'selection_mode', 'select_employee_ids', 'category_ids')
    def _compute_employee_ids(self):
        for wizard in self:
            domain = wizard.get_employees_domain()
            wizard.employee_ids = self.env['hr.employee'].search(domain)

    @api.depends('structure_type_ids')
    def _compute_structure_id(self):
        for wizard in self:
            wizard.structure_id = wizard.structure_type_ids[0].default_struct_id if wizard.structure_type_ids else False

    def get_employees_domain(self):
        domain = self._get_available_contracts_domain()
        if self.selection_mode == 'employee' and self.select_employee_ids:
            domain = expression.AND([
                domain,
                [('id', 'in', self.select_employee_ids.ids)]
            ])
        elif self.selection_mode == 'department' and self.department_ids:
            domain = expression.AND([
                domain,
                [('department_id', 'child_of', self.department_ids.ids)]
            ])
        elif self.selection_mode == 'structure' and self.structure_type_ids:
            domain = expression.AND([
                domain,
                [('contract_ids.structure_type_id', 'in', self.structure_type_ids.ids)]
            ])
        elif self.selection_mode == 'job' and self.job_ids:
            domain = expression.AND([
                domain,
                [('job_id', 'in', self.job_ids.ids)]
            ])
        elif self.selection_mode == 'category' and self.category_ids:
            domain = expression.AND([
                domain,
                [('category_ids', 'in', self.category_ids.ids)]
            ])
        if self.structure_id:
            domain = expression.AND([
                domain,
                [('contract_ids.structure_type_id', '=', self.structure_id.type_id.id)]
            ])
        return domain

    def _filter_contracts(self, contracts):
        # Could be overriden to avoid having 2 'end of the year bonus' payslips, etc.
        return contracts

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            today = fields.Date.today()
            first_day = today + relativedelta(day=1)
            last_day = today + relativedelta(day=31)
            if from_date == first_day and end_date == last_day:
                batch_name = from_date.strftime('%B %Y')
            else:
                batch_name = _('From %(from_date)s to %(end_date)s', from_date=format_date(self.env, from_date), end_date=format_date(self.env, end_date))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': batch_name,
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        #Prevent a payslip_run from having multiple payslips for the same employee
        employees -= payslip_run.slip_ids.employee_id
        success_result = {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
        if not employees:
            payslip_run.slip_ids.write({'state': 'verify'})
            payslip_run.state = 'verify'
            return success_result

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close']
        ).filtered(lambda c: c.active)
        contracts.generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end + relativedelta(days=1)),
            ('date_stop', '>=', payslip_run.date_start + relativedelta(days=-1)),
            ('employee_id', 'in', employees.ids),
        ])
        for slip in payslip_run.slip_ids:
            slip_tz = pytz.timezone(slip.contract_id.resource_calendar_id.tz or self.employee_id.tz or self.company_id.resource_calendar_id.tz or 'UTC')
            utc = pytz.timezone('UTC')
            date_from = slip_tz.localize(datetime.combine(slip.date_from, time.min)).astimezone(utc).replace(tzinfo=None)
            date_to = slip_tz.localize(datetime.combine(slip.date_to, time.max)).astimezone(utc).replace(tzinfo=None)
            payslip_work_entries = work_entries.filtered_domain([
                ('contract_id', '=', slip.contract_id.id),
                ('date_stop', '<=', date_to),
                ('date_start', '>=', date_from),
            ])
            payslip_work_entries._check_undefined_slots(slip.date_from, slip.date_to)

        if self.structure_id.type_id.default_struct_id == self.structure_id:
            work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
            if work_entries._check_if_error():
                work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])

                for work_entry in work_entries.filtered(lambda w: w.state == 'conflict'):
                    work_entries_by_contract[work_entry.contract_id] |= work_entry

                for work_entries in work_entries_by_contract.values():
                    conflicts = work_entries._to_intervals()
                    time_intervals_str = "".join(f"\n - {start} -> {end} ({entry.employee_id.name})" for start, end, entry in conflicts._items)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Some work entries could not be validated.'),
                        'message': _('Time intervals to look for:%s', time_intervals_str),
                        'sticky': False,
                    }
                }


        default_values = Payslip.default_get(Payslip.fields_get())
        payslips_vals = []
        for contract in self._filter_contracts(contracts):
            values = dict(default_values, **{
                'name': _('New Payslip'),
                'employee_id': contract.employee_id.id,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslips_vals.append(values)
        payslips = Payslip.with_context(tracking_disable=True).create(payslips_vals)
        payslips._compute_name()
        payslips.compute_sheet()
        payslip_run.slip_ids.write({'state': 'verify'})
        payslip_run.state = 'verify'

        return success_result
