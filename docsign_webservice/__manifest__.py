# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Sign Webservice",
    "version": "13.0.1.0.0",
    "category": "Web Service",
    "author": "Ecosoft",
    "summary": "This module call service e-Tax and Sign document",
    "license": "AGPL-3",
    "website": "http://ecosoft.co.th",
    "depends": [
        "docsign_account_printing",
        "docsign_template_form",
    ],
    "data": [
        "data/defaults.xml",
        "views/account_printing_views.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
