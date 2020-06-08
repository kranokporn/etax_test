# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Template Form",
    "version": "13.0.1.0.0",
    "category": "Form",
    "author": "Ecosoft",
    "summary": "Templates service eTax",
    "license": "AGPL-3",
    "website": "http://ecosoft.co.th",
    "depends": ["web", "docsign_account_printing"],
    "data": [
        "templates/report_templates.xml",
        "templates/crossindustryinvoice.xml",
        "templates/printing_pdf.xml",
        "templates/printing_text.xml",
        "data/account_reports.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
