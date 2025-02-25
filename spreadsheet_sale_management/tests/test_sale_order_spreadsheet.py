# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo.tests.common import TransactionCase, new_test_user


class SaleOrderSpreadsheet(TransactionCase):

    def test_sale_order_action_open(self):
        spreadsheet = self.env["sale.order.spreadsheet"].create({"name": "spreadsheet"})
        quotation_template = self.env["sale.order.template"].create({
            "name": "Test template",
            "spreadsheet_template_id": spreadsheet.id
        })
        sale_order = self.env["sale.order"].create({
            "partner_id": self.env.user.partner_id.id,
            "sale_order_template_id": quotation_template.id
        })
        self.assertFalse(sale_order.spreadsheet_ids)
        action = sale_order.action_open_sale_order_spreadsheet()
        self.assertEqual(action["tag"], "action_sale_order_spreadsheet")
        self.assertTrue(sale_order.spreadsheet_ids)
        self.assertEqual(sale_order.spreadsheet_ids.id, action["params"]["spreadsheet_id"])

    def test_sale_order_action_open_twice(self):
        spreadsheet = self.env["sale.order.spreadsheet"].create({"name": "spreadsheet"})
        quotation_template = self.env["sale.order.template"].create({
            "name": "Test template",
            "spreadsheet_template_id": spreadsheet.id
        })
        sale_order = self.env["sale.order"].create({
            "partner_id": self.env.user.partner_id.id,
            "sale_order_template_id": quotation_template.id
        })
        sale_order.action_open_sale_order_spreadsheet()
        spreadsheets = sale_order.spreadsheet_ids
        sale_order.action_open_sale_order_spreadsheet()
        self.assertEqual(sale_order.spreadsheet_ids, spreadsheets, "it should be the same spreadsheet")

    def test_get_selector_spreadsheet_models(self):
        user = new_test_user(self.env, login="Raoul")
        result = self.env["spreadsheet.mixin"].with_user(user).get_selector_spreadsheet_models()
        self.assertFalse(any(r["model"] == "sale.order.spreadsheet" for r in result))

        user.group_ids |= self.env.ref("sales_team.group_sale_salesman")
        result = self.env["spreadsheet.mixin"].with_user(user).get_selector_spreadsheet_models()
        self.assertTrue(any(r["model"] == "sale.order.spreadsheet" for r in result))

    def test_sale_order_spreadsheet_deleted_with_related_order(self):
        spreadsheet = self.env["sale.order.spreadsheet"].create({"name": "spreadsheet"})
        quotation_template = self.env["sale.order.template"].create({
            "name": "Test template",
            "spreadsheet_template_id": spreadsheet.id
        })
        sale_order = self.env["sale.order"].create({
            "partner_id": self.env.user.partner_id.id,
            "sale_order_template_id": quotation_template.id
        })
        sale_order.action_open_sale_order_spreadsheet()
        so_spreadsheet = sale_order.spreadsheet_ids
        sale_order.unlink()
        self.assertFalse(so_spreadsheet.exists(), "spreadsheet should be deleted with the related order")
        self.assertTrue(spreadsheet.exists(), "Original spreadsheet should be unaltered")
