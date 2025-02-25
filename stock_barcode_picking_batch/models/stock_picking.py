
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"
    display_batch_button = fields.Boolean(compute='_compute_display_batch_button')

    @api.depends('batch_id')
    def _compute_display_batch_button(self):
        for picking in self:
            picking.display_batch_button = picking.batch_id and picking.batch_id.state == 'in_progress'

    def action_open_batch_picking(self):
        self.ensure_one()
        return self.batch_id.action_client_action()

    def action_unbatch(self):
        self.ensure_one()
        if self.batch_id:
            self.batch_id = False

    def _get_without_quantities_error_message(self):
        if self.env.context.get('barcode_view'):
            return _(
                'You cannot validate a transfer if no quantities are reserved nor done. '
                'You can use the info button on the top right corner of your screen '
                'to remove the transfer in question from the batch.'
            )
        else:
            return super()._get_without_quantities_error_message()


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    group_lines_by_product = fields.Boolean("Group batch lines", help="Lines of same product at same location appear grouped. Not to use for cluster picking")

    def action_picking_batch_barcode_kanban(self):
        action = self._get_action('stock_barcode_picking_batch.stock_barcode_batch_picking_action_kanban')
        return action

    def _get_barcode_config(self):
        config = super()._get_barcode_config()
        config['group_lines_by_product'] = self.group_lines_by_product
        return config

    def get_model_records_count(self, res_model):
        self.ensure_one()
        assert res_model in ['stock.picking', 'stock.picking.batch']

        if res_model == 'stock.picking':
            return self.count_picking_ready

        return self.env['stock.picking.batch'].search_count([
            ('picking_type_id', '=', self.id),
            ('user_id', 'in', [self.env.user.id, False]),
            ('state', '=', 'in_progress'),
        ])
