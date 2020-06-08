# Copyright 2020 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def render_qweb_text(self, docids, data=None):
        """
            Delete space and Convert HTML Entities to characters
        """
        res = super().render_qweb_text(docids, data)
        lst = list(res)
        lst[0] = lst[0].strip()
        lst[0] = lst[0].replace(b"&quot;", b'"')
        res = tuple(lst)
        return res
