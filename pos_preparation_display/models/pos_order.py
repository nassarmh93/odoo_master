import json

from odoo import models, api
from functools import reduce


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def sync_from_ui(self, orders):
        data = super().sync_from_ui(orders)

        if len(orders) > 0:
            orders = self.browse([o['id'] for o in data["pos.order"]])
            for order in orders:
                if order.state == 'paid' and not order.config_id.module_pos_restaurant:
                    self.env['pos_preparation_display.order'].process_order(order.id)

        # When preparation context is defined only one order is available in data
        if self.env.context.get('preparation'):
            options = self.env.context.get('preparation').get('process_order_options')
            order = self.browse(data["pos.order"][0]['id'])
            self.env['pos_preparation_display.order'].process_order(order.id, options)
            order.config_id.notify_synchronisation(order.config_id.current_session_id.id, self.env.context.get('login_number', 0))

        return data

    def _process_preparation_changes(self, options):
        self.ensure_one()
        flag_change = False
        flag_order_added = False
        sound = False
        cancelled = options.get('cancelled', False)
        general_customer_note = options.get('general_customer_note', None)
        note_history = options.get('note_history', None)
        internal_note = options.get('internal_note', None)

        pdis_order = self.env['pos_preparation_display.order'].search(
            [('pos_order_id', '=', self.id)]
        )

        pdis_lines = pdis_order.preparation_display_order_line_ids
        pdis_ticket = False
        quantity_data = {}
        category_ids = set()
        lopc_lines = {}   # last_order_preparation_change lines
        if self.last_order_preparation_change:
            lopc = json.loads(self.last_order_preparation_change)
            lopc_lines = lopc.get('lines', {})

        unmerged_lines = reduce(
            lambda acc, line: {**acc, line["uuid"]: line["order_id"]},
            self.env["pos.order.line"].search_read([("uuid", "in", pdis_lines.mapped("pos_order_line_uuid"))], ["uuid", "order_id"], load=False),
            {}
        )
        # If cancelled flag, we flag all lines as cancelled
        if cancelled:
            for line in pdis_lines:
                line.product_cancelled = line.product_quantity
                category_ids.update(line.product_id.pos_categ_ids.ids)
            return {'change': True, 'sound': False, 'category_ids': category_ids}

        order_line_filter = self._context.get('ppc_order_line_filter', lambda x: True)
        # create a dictionary with the key as a tuple of product_id, internal_note and attribute_value_ids
        for pdis_line in pdis_lines:
            key = (pdis_line.product_id.id, pdis_line.internal_note or '', json.dumps(pdis_line.attribute_value_ids.ids), pdis_line.pos_order_line_uuid)
            line_qty = pdis_line.product_quantity - pdis_line.product_cancelled
            # Ensure that when an orderline is merged to another table (e.g., from Table 1 to Table 2), sent to the kitchen,
            # and later unmerged back to its original table, it is not canceled if the order is sent to the kitchen again from Table 2.
            unmerged_line_order_id = unmerged_lines.get(pdis_line.pos_order_line_uuid)
            if unmerged_line_order_id and unmerged_line_order_id != self.id:
                continue
            if not quantity_data.get(key):
                quantity_data[key] = {
                    'attribute_value_ids': pdis_line.attribute_value_ids.ids,
                    'note': pdis_line.internal_note or '',
                    'product_id': pdis_line.product_id.id,
                    'display': line_qty,
                    'order': 0,
                    'uuid': pdis_line.pos_order_line_uuid,
                }
            else:
                quantity_data[key]['display'] += line_qty

        for line in self.lines:
            line_note = line.note or ""
            key = (line.product_id.id, line_note, json.dumps(line.attribute_value_ids.ids), line.uuid)

            # Prevents quantity increase when an orderline is transferred to another table but was originally ordered in a previous table.
            transferred_qty = lopc_lines.get(line.uuid + ' - ' + (line.note or ''), {}).get("transferredQty", 0)
            if not quantity_data.get(key):
                quantity_data[key] = {
                    'attribute_value_ids': line.attribute_value_ids.ids,
                    'note': line_note or '',
                    'product_id': line.product_id.id,
                    'display': 0,
                    'order': line.qty - transferred_qty,
                    'uuid': line.uuid,
                }
            else:
                quantity_data[key]['order'] += line.qty - transferred_qty

        # Update quantity_data with note_history
        if note_history:
            for line in pdis_lines[::-1]:
                product_id = str(line.product_id.id)
                for note in note_history.get(product_id, []):
                    if note["uuid"] == line.pos_order_line_uuid and line.internal_note == note['old'] and note['qty'] > 0 and line.product_quantity <= note['qty'] - note.get('used_qty', 0):
                        if not note.get('used_qty'):
                            note['used_qty'] = line.product_quantity
                        else:
                            note['used_qty'] += line.product_quantity

                        key = (line.product_id.id, line.internal_note or '', json.dumps(line.attribute_value_ids.ids), line.pos_order_line_uuid)
                        key_new = (line.product_id.id, note['new'] or '', json.dumps(line.attribute_value_ids.ids), line.pos_order_line_uuid)

                        line.internal_note = note['new']
                        flag_change = True
                        category_ids.update(line.product_id.pos_categ_ids.ids)

                        if not quantity_data.get(key_new):
                            quantity_data[key_new] = {
                                'attribute_value_ids': line.attribute_value_ids.ids,
                                'note': note['new'] or '',
                                'product_id': line.product_id.id,
                                'display': 0,
                                'order': 0,
                                'uuid': line.pos_order_line_uuid,
                            }

                        # Merge the two lines, so that if the quantity was changed it's also applied
                        old_quantity = quantity_data.pop(key, None)
                        quantity_data[key_new]["display"] += old_quantity["display"]
                        quantity_data[key_new]["order"] += old_quantity["order"]

        # Check if pos_order have new lines or if some lines have more quantity than before
        if any([quantities['order'] > quantities['display'] and order_line_filter(quantities['uuid']) for quantities in quantity_data.values()]):
            flag_change = True
            flag_order_added = True
            sound = True
            pdis_ticket = self.env['pos_preparation_display.order'].create({
                'displayed': True,
                'pos_order_id': self.id,
                'pos_config_id': self.config_id.id,
                'pdis_general_customer_note': self.general_customer_note or '',
                'pdis_internal_note': self.internal_note or '',
            })

        product_ids = self.env['product.product'].browse([data['product_id'] for data in quantity_data.values()])

        for data in quantity_data.values():
            product_id = data['product_id']
            product = product_ids.filtered(lambda p: p.id == product_id)
            if data['order'] > data['display']:
                missing_qty = data['order'] - data['display']
                filtered_lines = self.lines.filtered(lambda li: li.uuid == data['uuid'] and order_line_filter(li.uuid))
                line_qty = 0

                for line in filtered_lines:

                    if missing_qty == 0:
                        break

                    if missing_qty > line.qty:
                        line_qty += line.qty
                        missing_qty -= line.qty
                    elif missing_qty <= line.qty:
                        line_qty += missing_qty
                        missing_qty = 0

                    if missing_qty == 0 and line_qty > 0:
                        flag_change = True
                        flag_order_added = True
                        category_ids.update(product.pos_categ_ids.ids)

                        parent = False
                        if line.combo_parent_id:
                            parent_line = self.lines.filtered(lambda l: l.id == line.combo_parent_id.id)
                            parent = self.env['pos_preparation_display.orderline'].search([
                                ('pos_order_line_uuid', '=', parent_line.uuid),
                                ('preparation_display_order_id', '=', pdis_ticket.id)
                            ], limit=1)

                        self.env['pos_preparation_display.orderline'].create({
                            'todo': True,
                            'internal_note': line.note or "",
                            'attribute_value_ids': line.attribute_value_ids.ids,
                            'product_id': product_id,
                            'product_quantity': line_qty,
                            'preparation_display_order_id': pdis_ticket.id,
                            'pos_order_line_uuid': line.uuid,
                            'combo_parent_id': parent.id if parent else False
                        })

            elif data['order'] < data['display']:
                qty_to_cancel = data['display'] - data['order']
                for line in pdis_lines.filtered(lambda li: li.product_id.id == product_id and li.internal_note == data['note'] and li.attribute_value_ids.ids == data['attribute_value_ids'] and li.pos_order_line_uuid == data['uuid']):
                    flag_change = True
                    line_qty = 0
                    pdis_qty = line.product_quantity - line.product_cancelled

                    if qty_to_cancel == 0:
                        break

                    if pdis_qty > qty_to_cancel:
                        line.product_cancelled += qty_to_cancel
                        qty_to_cancel = 0
                    elif pdis_qty <= qty_to_cancel:
                        line.product_cancelled += pdis_qty
                        qty_to_cancel -= pdis_qty
                    category_ids.update(line.product_id.pos_categ_ids.ids)

        if general_customer_note is not None:
            for order in pdis_order:
                if order.pdis_general_customer_note != general_customer_note:
                    order.pdis_general_customer_note = general_customer_note or ''
                    flag_change = True
                    category_ids.update(pdis_lines[0].product_id.pos_categ_ids.ids)  # necessary to send when only ordernote changed
        if internal_note is not None:
            for order in pdis_order:
                if order.pdis_internal_note != internal_note:
                    order.pdis_internal_note = internal_note or ''
                    flag_change = True
                    category_ids.update(pdis_lines[0].product_id.pos_categ_ids.ids)  # necessary to send when only ordernote changed

        return {'change': flag_change, 'sound': sound, 'category_ids': category_ids, 'order_added': flag_order_added}
