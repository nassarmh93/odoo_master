from odoo.tests import TransactionCase
from odoo.exceptions import UserError


class TestSalaryRuleCategory(TransactionCase):

    def setUp(self):
        super().setUp()

        self.existing_category1 = self.env['hr.salary.rule.category'].create({
            'name': 'Existing Category',
            'code': 'EXIST',
            'country_id': self.env.ref('base.fr').id,
        })

        self.existing_category2 = self.env['hr.salary.rule.category'].create({
            'name': 'No Country Category',
            'code': 'NOCOUNTRY',
            'country_id': False,
        })

    def test_create_category_with_same_code(self):
        with self.assertRaises(UserError):
            self.env['hr.salary.rule.category'].create({
                'name': 'New Category',
                'code': 'EXIST',
                'country_id': self.env.ref('base.fr').id,
            })

        with self.assertRaises(UserError):
            self.env['hr.salary.rule.category'].create({
                'name': 'Another New Category',
                'code': 'NOCOUNTRY',
                'country_id': False,
            })

    def test_create_category_with_country_and_no_country(self):
        with self.assertRaises(UserError):
            self.env['hr.salary.rule.category'].create({
                'name': 'Country Specific',
                'code': 'NOCOUNTRY',
                'country_id': self.env.ref('base.fr').id,
            })

        with self.assertRaises(UserError):
            self.env['hr.salary.rule.category'].create({
                'name': 'Countryless',
                'code': 'EXIST',
                'country_id': False,
            })

    def test_create_category_with_duplicate_code_in_different_country(self):
        category = self.env['hr.salary.rule.category'].create({
            'name': 'Different Country Category',
            'code': 'EXIST',
            'country_id': self.env.ref('base.be').id,
        })
        self.assertTrue(category)

    def test_create_category_with_unique_code(self):
        category = self.env['hr.salary.rule.category'].create({
            'name': 'Unique Category',
            'code': 'UNIQUE_CODE',
            'country_id': self.env.ref('base.be').id,
        })
        self.assertTrue(category)
