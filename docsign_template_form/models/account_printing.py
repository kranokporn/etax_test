# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo import models


DEFAULT_FACTURX_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


class AccountPrinting(models.Model):
    _inherit = "account.printing"

    def _get_params(self, param):
        self.ensure_one()
        icp = self.env['ir.config_parameter'].sudo()
        param = icp.get_param('webservice.%s' % param)
        return param

    def format_date(self, dt):
        # Format the date in the eTax standard.
        dt = dt or datetime.now()
        return dt.strftime(DEFAULT_FACTURX_DATE_FORMAT)

    def _create_text_config(self, docs):
        for obj in docs:
            text = '"C" "{}" "{}" "{}_{}.txt"\n'.format(
                obj._get_params('sellertaxid'),
                obj._get_params('sellerbranchid'),
                obj._get_params('sellertaxid'),
                obj._get_params('sellerbranchid')
            )
        return text

    def _create_text_header(self, docs):
        for obj in docs:
            text = '{} {} "{}" "{}" {} "{}" {} {} {} {} {}\n'.format(
                obj.cert_id.supplier_partner_id.vat or "",
                obj.cert_id.supplier_partner_id.display_name or "",
                obj.cert_id.supplier_partner_id.street or "",
                obj.cert_id.date,
                obj.wt_cert_income_desc or "",
                "{:,.2f}".format(obj.wt_percent / 100) or 0.00,
                "{:,.2f}".format(obj.base) or 0.00,
                "{:,.2f}".format(obj.amount) or 0.00,
                obj.cert_id.tax_payer,
                obj.cert_id.payment_id.display_name,
            )
        return text
