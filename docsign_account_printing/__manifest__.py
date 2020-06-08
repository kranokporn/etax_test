# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Sign Account Printing",
    "version": "13.0.1.0.0",
    "category": "Accounting & Report",
    "author": "Ecosoft",
    "summary": "New menu e-Tax for sign.",
    "license": "AGPL-3",
    "website": "http://ecosoft.co.th",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_printing_views.xml",
        "views/printing_menuitem.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
