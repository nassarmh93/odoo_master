from lxml import etree, objectify

from odoo import models, release, _
from odoo.tools import float_round
from odoo.addons.l10n_cz_reports.models import l10n_cz_reports_utils as cz_utils


class CzechTaxReportCustomHandler(models.AbstractModel):
    """
        Generate the VAT report for the Czech Republic.
        Generated using as a reference the documentation at
        https://adisspr.mfcr.cz/dpr/adis/idpr_pub/epo2_info/popis_struktury_detail.faces?zkratka=DPHDP3
    """
    _name = 'l10n_cz.tax.report.handler'
    _inherit = 'account.tax.report.handler'
    _description = 'Czech Tax Report Custom Handler'

    def _custom_options_initializer(self, report, options, previous_options):
        super()._custom_options_initializer(report, options, previous_options=previous_options)

        options.setdefault('buttons', []).append({
            'name': _('XML'),
            'sequence': 30,
            'action': 'export_file',
            'action_param': 'export_to_xml',
            'file_export_type': _('XML'),
        })

    def export_to_xml(self, options):
        report = self.env['account.report'].browse(options['report_id'])
        sender_company = report._get_sender_company_for_export(options)
        cz_utils.validate_czech_company_fields(sender_company)

        report_options = report.get_options(previous_options={**options, 'export_mode': 'file'})
        report_lines = report._get_lines(report_options)

        values = {}
        for line in report_lines:
            if not line['code']:
                continue
            values[line['code']] = {}
            for col in line['columns']:
                values[line['code']][col['expression_label']] = float_round(col['no_format'], precision_digits=0) if col['no_format'] is not None else 0

        data = {
            'odoo_version': release.version,
            'veta_d': cz_utils.get_veta_d_vals(report, options),
            'veta_p': cz_utils.get_veta_p_vals(sender_company),
            **values,
        }
        xml_content = self.env['ir.qweb']._render('l10n_cz_reports.cz_tax_report_template', values=data)
        tree = objectify.fromstring(xml_content)
        formatted_xml = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        return {
            'file_name': report.get_default_report_filename(options, 'xml'),
            'file_content': formatted_xml,
            'file_type': 'xml',
        }
