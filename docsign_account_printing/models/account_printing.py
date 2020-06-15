# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields

REASON_PURPOSE = [
    ('DBNG01', 'มีการเพิ่มราคาค่าสินค้า (สินค้าเกินกว่าจำนวนที่ตกลงกัน)'),
    ('DBNG02', 'คำนวณราคาสินค้า ผิดพลาดต่ำกว่าที่เป็นจริง'),
    ('DBNG99', 'เหตุอื่น (ระบุสาเหตุ)'),
    ('DBNS01', 'การเพิ่มราคาค่าบริการ (บริการเกินกว่าข้อกำหนดทตกลงกัน)'),
    ('DBNS02', 'คำนวณราคาค่าบริการ ผิดพลาดต่ำกว่าที่เป็นจริง'),
    ('DBNS99', 'เหตุอื่น (ระบุสาเหตุ)'),
    ('CDNG01', 'ลดราคาสินค้าที่ขาย (สินค้าผิดข้อกำหนดที่ตกลงกัน)'),
    ('CDNG02', 'สินค้าชำรุดเสียหาย'),
    ('CDNG03', 'สินค้าขาดจำนวนตามที่ตกลงซื้อขาย'),
    ('CDNG04', 'คำนวณราคาสินค้าผิดพลาดสูงกว่าที่เป็นจริง'),
    ('CDNG05', 'รับคืนสินค้า (ไม่ตรงตามคำพรรณนา)'),
    ('CDNG99', 'เหตุอื่น (ระบุสาเหตุ)'),
    ('CDNS01', 'ลดราคาค่าบริการ (บริการผิดข้อกำหนดที่ตกลงกัน)'),
    ('CDNS02', 'ค่าบริการขาดจำนวน'),
    ('CDNS03', 'คำนวณราคาค่าบริการผิดพลาดสูงกว่าที่เป็นจริง'),
    ('CDNS04', 'บอกเลิกสัญญาบริการ'),
    ('CDNS99', 'เหตุอื่น (ระบุสาเหตุ)'),
    ('TIVC01', 'ชื่อผิด'),
    ('TIVC02', 'ที่อยู่ผิด'),
    ('TIVC99', 'เหตุอื่น (ระบุสาเหตุ)'),
    ('RCTC01', 'ชื่อผิด'),
    ('RCTC02', 'ที่อยู่ผิด'),
    ('RCTC03', 'รับคืนสินค้า / ยกเลิกบริการ ทั้งจำนวน (ระบุจำนวนเงิน) บาท'),
    ('RCTC04', 'รับคืนสินค้า / ยกเลิกบริการ บางส่วนจำนวน (ระบุจำนวนเงิน) บาท'),
    ('RCTC99', 'เหตุอื่น (ระบุสาเหตุ)'),
]


class AccountPrinting(models.Model):
    _name = "account.printing"
    _inherit = ["mail.thread"]
    _description = "Printing for eTax"

    number = fields.Char(default="/", required=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env.company.id, ondelete='cascade')
    # header
    customer_name = fields.Char(string="Customer")
    date_document = fields.Datetime()
    operating_unit = fields.Char()
    currency = fields.Many2one(comodel_name="res.currency")
    system_origin_name = fields.Char(string="System Origin Name")
    system_origin_number = fields.Char(string="System Origin Number")
    origin_id = fields.Many2one(comodel_name="account.printing")
    user_sign = fields.Char(string="User")
    # purpose document signed
    purpose_code = fields.Char()
    purpose_name = fields.Selection(
        REASON_PURPOSE, compute="_compute_reason", string="Purpose")
    purpose_reason_other = fields.Text(string="Reason Other")

    # Customer Information
    customer_street = fields.Char()
    customer_street2 = fields.Char()
    customer_city = fields.Char()
    customer_state = fields.Char()
    customer_zip = fields.Char()
    customer_country_code = fields.Char()
    customer_vat = fields.Char()
    customer_phone = fields.Char()
    customer_email = fields.Char()

    # Seller Information
    seller_name = fields.Char(string="Seller")
    seller_street = fields.Char()
    seller_street2 = fields.Char()
    seller_city = fields.Char()
    seller_state = fields.Char()
    seller_zip = fields.Char()
    seller_country_code = fields.Char()
    seller_vat = fields.Char()
    seller_phone = fields.Char()
    seller_email = fields.Char()

    # Tax Branch
    taxbranch_name = fields.Char()
    taxbranch_code = fields.Char()
    taxbranch_taxid = fields.Char(string="Tax ID")

    state = fields.Selection(selection=[
            ('draft', 'Waiting'),
            ('signed', 'Signed'),
            ('cancel', 'Cancelled'),
            ('preview', 'Preview'),
            ('exception', 'Exception'),
        ], string='Status', required=True, readonly=True,
        copy=False, tracking=True, default='draft',
        help="Waiting: New Document or Can't sign this document\n\
              Signed: Document signed\n\
              Cancelled: Old document signed\n\
              Preview: Document show preview only\n\
              Exception : Signed Error"
    )

    # lines
    printing_lines = fields.One2many(
        comodel_name='account.printing.line',
        inverse_name='printing_id',
        string="Printing Lines",
        copy=True
    )
    # === Amount fields ===
    amount_untaxed = fields.Float(
        string='Untaxed Amount', readonly=True, tracking=True)
    amount_tax = fields.Float(string='Tax', readonly=True)
    amount_total = fields.Float(string='Total', readonly=True)

    notes = fields.Text()

    def _compute_reason(self):
        for rec in self:
            rec.purpose_name = rec.purpose_code
        return True

    def action_post(self):
        self.write({'state': 'signed'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def action_set_to_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.model
    def create(self, values):
        """
            Create New Number, Origin and System Origin
            Example :
            ===================================================================
            Number   Process             Number Server  Origin    System Origin
            ===================================================================
            DV00001  --(Sign)-->         DV00001        DV00001     DV00001
            DV00001  --(Update Sign)-->  DV00001_1      DV00001     DV00001
            DV00001  --(Update Sign)-->  DV00001_2      DV00001_1   DV00001
            DV00001  --(Update Sign)-->  DV00001_3      DV00001_2   DV00001
        """
        res = super().create(values)
        duplicate = self.search([
            ('system_origin_number', '=', res.number),
            ('state', 'not in', ['preview', 'exception'])], order='id desc')
        res.write({'system_origin_number': res.number})
        # convert number to pattern <number>_<number of duplicate>
        if duplicate and res.state not in ('preview', 'exception'):
            res.write({
                'number': '%s_%s' % (res.number, len(duplicate)),
                'origin_id': duplicate[0].id
            })
        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([
                ("number", "=", name),
                ("state", "not in", ["preview", "exception"])
            ] + args, limit=limit)
        if not recs:
            recs = self.search([
                ("number", operator, name),
                ("state", "not in", ["preview", "exception"])
            ] + args, limit=limit)
        return recs.name_get()

    def name_get(self):
        result = [(rec.id, rec.number) for rec in self]
        return result


class AccountPrintingLines(models.Model):
    _name = "account.printing.line"
    _description = "Line of Printing"

    printing_id = fields.Many2one(
        comodel_name="account.printing",
        ondelete="cascade",
    )

    product_name = fields.Char(string="Product")
    name = fields.Text(string="Description")
    activity_group_name = fields.Char(string="Activity Group")
    quantity = fields.Float()
    uom = fields.Char(string="Unit of Measure")
    price_unit = fields.Float(string="Unit Price")
    taxes = fields.Char()
    price_subtotal = fields.Float(string="Amount")
