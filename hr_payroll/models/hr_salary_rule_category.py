# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression


class HrSalaryRuleCategory(models.Model):
    _name = 'hr.salary.rule.category'
    _description = 'Salary Rule Category'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    parent_id = fields.Many2one('hr.salary.rule.category', string='Parent',
        help="Linking a salary category to its parent is used only for the reporting purpose.",
        domain="['|', ('country_id', '=', False), ('country_id', '=', country_id)]")
    children_ids = fields.One2many('hr.salary.rule.category', 'parent_id', string='Children')
    note = fields.Html(string='Description')
    country_id = fields.Many2one(
        'res.country',
        string="Country",
        default=lambda self: self.env.company.country_id,
        domain=lambda self: [('id', 'in', self.env.companies.country_id.ids)]
    )

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(_('Error! You cannot create recursive hierarchy of Salary Rule Category.'))

    @api.constrains('country_id')
    def _check_rule_category_country(self):
        for category in self:
            if category.country_id and self.env['hr.salary.rule'].sudo().search_count([('category_id', '=', category.id), ('country_id', '!=', category.country_id.id)], limit=1):
                raise UserError(_('You cannot change the country of category %s as it is used in existing Salary Rules', category.name))

    @api.constrains('code', 'country_id')
    def _check_rule_category_name_code_country(self):
        domain = [('code', 'in', self.mapped('code')), ('id', 'not in', self.ids)]
        if self.country_id:
            domain = expression.AND([domain, [('country_id', 'in', [False] + self.country_id.ids)]])
        existing_category = self.env['hr.salary.rule.category'].sudo().search_count(domain, limit=1)
        if existing_category:
            raise UserError(_('You cannot create Salary Rule Category with the same code within the same country.'))

    def _sum_salary_rule_category(self, localdict, amount):
        self.ensure_one()
        if self.parent_id:
            localdict = self.parent_id._sum_salary_rule_category(localdict, amount)
        localdict['categories'][self.code] = localdict['categories'][self.code] + amount
        return localdict
