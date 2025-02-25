# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import  api, models, fields, _
from odoo.exceptions import ValidationError

class SaleCommissionAchievement(models.Model):
    _inherit = 'sale.commission.achievement'

    add_user_id = fields.Many2one('sale.commission.plan.user', "Add to",
        domain=[('plan_id.active', '=', True)]
    )
    reduce_user_id = fields.Many2one('sale.commission.plan.user', "Reduce From",
        domain=[('plan_id.active', '=', True)],
    )
    achieved = fields.Monetary("Achieved", currency_field='currency_id')


    @api.constrains('add_user_id', 'reduce_user_id', 'company_id', 'date')
    def _constraint_unique(self):
        res = self._read_group(
            domain=[],
            groupby=['add_user_id', 'reduce_user_id', 'company_id', 'date:month'],
            aggregates=['__count']
        )
        for val in res:
            count = val[-1]
            if count > 1:
                raise ValidationError(_("The adjustments must be unique by user, team, company, achievement and date (month)"))
