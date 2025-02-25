# Part of Odoo. See LICENSE file for full copyright and licensing details.
from markupsafe import Markup

from odoo import models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def write(self, vals):
        if 'state' in vals:
            self = self.filtered(lambda purchase_order: purchase_order.state != vals['state'])
            related_product_lines = self.sudo().env['approval.product.line'].search(
                domain=[('purchase_order_line_id.order_id', 'in', self.ids)],
            )
            grouped_product_lines = dict()
            for product_line in related_product_lines:
                approval_request_id = product_line.approval_request_id
                purchase_order_id = product_line.purchase_order_line_id.order_id
                if not grouped_product_lines.get(approval_request_id):
                    grouped_product_lines[approval_request_id] = dict()
                if not grouped_product_lines[approval_request_id].get(purchase_order_id):
                    grouped_product_lines[approval_request_id][purchase_order_id] = self.env['approval.product.line']
                grouped_product_lines[approval_request_id][purchase_order_id] |= product_line

            self._log_po_state_change_to_approval_request_chatter(vals['state'], grouped_product_lines)
        return super().write(vals)

    def _log_po_state_change_to_approval_request_chatter(self, new_state, grouped_product_lines):
        for approval_request, product_lines_by_purchase_order in grouped_product_lines.items():
            for purchase_order, product_lines in product_lines_by_purchase_order.items():
                state_change_msg = purchase_order._create_state_change_msg(purchase_order.state, new_state, product_lines)
                approval_request._message_log(body=state_change_msg)

    def _create_state_change_msg(self, old_state, new_state, approval_request_products):
        state_label = dict(self._fields['state']._description_selection(self.env))
        return Markup("%(state_change_header)s<br> %(products_summary)s") % {
            'state_change_header': _("RFQ %(rfq_name)s state has been changed: %(old_state_label)s -> %(new_state_label)s",
                rfq_name=self.name,
                old_state_label=state_label[old_state],
                new_state_label=state_label[new_state]),
            'products_summary': Markup("%(header)s<br> <ul>%(products)s</ul>") % {
                'header': _("Products: "),
                'products': Markup().join(
                    Markup("<li>%(product_quantity)s %(product_name)s</li>") % {
                        'product_quantity': product.quantity,
                        'product_name': product.product_id.name
                    } for product in approval_request_products
                )
            }
        }
