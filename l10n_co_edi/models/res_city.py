# coding: utf-8

from odoo import fields, models


class ResCity(models.Model):
    _inherit = 'res.city'

    l10n_co_edi_code = fields.Integer("EDI City Code")
