# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import requests
import base64
import ast
import urllib
from datetime import datetime
from odoo import api, models, _
from odoo.tools import float_repr

_logger = logging.getLogger(__name__)

DEFAULT_FACTURX_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


class AccountPrinting(models.Model):
    _inherit = "account.printing"

    def _export_as_facturx_th_xml(self):
        ''' Create the Factur-x xml file content.
        :return: The XML content as str.
        '''
        self.ensure_one()

        def format_date(dt):
            # Format the date in the eTax standard.
            dt = dt or datetime.now()
            return dt.strftime(DEFAULT_FACTURX_DATE_FORMAT)

        def format_monetary(number, currency):
            # Format the monetary values to avoid trailing decimals
            # (e.g. 90.85000000000001).
            return float_repr(abs(number), 2)

        # Create file content.
        template_values = {
            'record': self,
            'format_date': format_date,
            'format_monetary': format_monetary,
        }
        content = self.env.ref(
            'docsign_template_form.account_printing_facturx_export'
            ).render(template_values)
        return b"<?xml version='1.0' encoding='UTF-8'?>\n \
                 <?template name='TIV0102' xslt='V10000'?>\n \
                 <?xml-model href='TaxInvoice_Schematron_2p0.sch' type='application/xml' schematypens='http://purl.oclc.org/dsdl/schematron'?>" \
                  + content

    def _update_state_preview(self, data_dict):
        for dict in data_dict:
            dict['state'] = 'preview'
        return data_dict

    def _get_link_pdf(self, attachment, download=False):
        config_obj = self.env['ir.config_parameter']
        base_url = config_obj.get_param('web.base.url')
        link_download = '%s/web/content/%s/%s' % (
            base_url, attachment.id, attachment.name)
        if download:
            link_download = '%s?download=true' % link_download
        return link_download

    def _generate_pdf_file(self):
        self.ensure_one()
        # generated pdf and xml
        # TODO: Form not fixed
        pdf_report = \
            self.env.ref('docsign_template_form.account_printing_pdf')
        pdf_content = pdf_report.render_qweb_pdf(self.id)[0]
        return pdf_content

    def _generate_xml_file(self):
        xml_content = self._export_as_facturx_th_xml()
        return xml_content

    def _generate_text_file(self):
        self.ensure_one()
        # generated pdf and xml
        # TODO: Form not fixed
        text_report = self.env.ref(
            'docsign_template_form.account_printing_text')
        text_content = text_report.render_qweb_text(self.id)[0].decode('utf-8')
        return text_content

    def _check_sign_pdf(self, data_dict):
        invoice_dict = []
        message = []
        for dict in data_dict:
            # search number
            # inv = self.search([
            #     ('number', '=', dict['number']),
            #     ('state', 'not in', ('preview', 'exception'))
            #     ], order="id desc")
            inv = self.search([
                ('number', '=', dict['number']),
                ('state', 'in', ('draft', 'signed'))],
                order="id desc")
            if inv and inv.filtered(lambda l: l.state == 'signed'):
                # case edit signed
                if dict['purpose_code']:
                    invoice_dict.append(dict)
                    continue
                number = inv[0].number
                message.append({
                    'name': number,
                    'link_download': False,
                    'status': 'FAILED',
                    'errorMessage': _('This Document %s signed.' % number)
                })
            # there are invoice state draft only
            elif inv:
                inv.unlink()
                invoice_dict.append(dict)
            # never create in server
            else:
                invoice_dict.append(dict)
        return invoice_dict, message

    def _get_data_connect_api_etax(self, icp):
        api = icp.get_param('webservice.api')
        usercode = icp.get_param('webservice.usercode')
        accesskey = icp.get_param('webservice.accesskey')
        sellertaxid = icp.get_param('webservice.sellertaxid')
        sellerbranchid = icp.get_param('webservice.sellerbranchid')
        servicecode = icp.get_param('webservice.servicecode')
        data = {
            'APIKey': api or False,
            'SellerTaxId': sellertaxid or False,
            'SellerBranchId': sellerbranchid or False,
            'UserCode': usercode or False,
            'AccessKey': accesskey or False,
            'ServiceCode': servicecode or False,
        }
        return data

    @api.model
    def generate_pdf_file_link(self, data_dict):
        """
            Add state to preview and create new document for preview only
        """
        attachment_obj = self.env['ir.attachment']
        message = []
        data_dict = self._update_state_preview(data_dict)
        invoice_printing_ids = self.create(data_dict)

        for rec in invoice_printing_ids:
            pdf_content = rec._generate_pdf_file()  # TODO: waitting form
            attachment = attachment_obj.create({
                'name': _("%s_preview.pdf") % rec.number,
                'type': 'binary',
                'datas': base64.encodestring(pdf_content),
                'res_model': rec._name,
                'res_id': rec.id,
                'public': True,  # for download
            })
            rec.message_post(body=_("Attachment created successfully."))
            link_preview = self._get_link_pdf(attachment)
            message.append({
                'name': rec.system_origin_number,
                'link_download': link_preview,
                'status': 'OK',
                'errorMessage': False,
            })
        return message

    @api.model
    def check_edit_value(self, data_dict):
        """
            Find invoice latest and check value change.
            if not change will return error.
        """
        message = []
        for dict in data_dict:
            # find invoice latest
            inv = self.search([
                ('system_origin_number', '=', dict['number']),
                ('state', '=', 'signed')], order="id desc", limit=1)
            # edit name
            if dict['purpose_code'] in ('RCTC01', 'TIVC01'):
                if inv.customer_name == dict['customer_name']:
                    message.append({
                        'status': 'ER',
                        'errorMessage':
                            'Document %s is name has not been changed.'
                            % dict['number']})
                else:
                    message.append({'status': 'OK'})
            # edit address
            # elif dict['purpose_code'] in ('RCTC02', 'TIVC02'):
            #     if condition:
            #         pass
            else:
                message.append({'status': 'OK'})
        return message

    @api.model
    def action_call_service(self, data_dict):
        """
            PABI2 / Myproperty / MySale / POS will send data to this method,
            then call API service to eTax and get link download and generated,
            finally, return datas back to origin.
        """
        icp = self.env['ir.config_parameter'].sudo()
        attachment_obj = self.env['ir.attachment']
        request_url = icp.get_param('webservice.url')
        printing_ok = []
        invoice_dict, message = self._check_sign_pdf(data_dict)
        # create invoice printing
        if invoice_dict:
            data = self._get_data_connect_api_etax(icp)
            invoice_printing_ids = self.create(invoice_dict)

            for rec in invoice_printing_ids:
                pdf_content = rec._generate_pdf_file()  # TODO: waitting form
                text_content = rec._generate_text_file()  # TODO: waitting form
                xml_content = rec._generate_xml_file()  # TODO: waitting form
                file = {
                    'TextContent': text_content,
                    'PDFContent': pdf_content,
                    'XMLContent': xml_content,
                }
                try:
                    responese = \
                        requests.post(request_url, data=data, files=file)
                    responese.raise_for_status()
                    # convert string to dict for get data
                    res = ast.literal_eval(responese.text)
                    if res['status'] == 'OK':
                        pdfurl = res['pdfURL']
                        pdf = urllib.request.urlopen(pdfurl).read()
                        # create attachment in odoo
                        attachment = attachment_obj.create({
                            'name': _("%s.pdf") % rec.number,
                            'type': 'binary',
                            'datas': base64.encodestring(pdf),
                            'res_model': rec._name,
                            'res_id': rec.id,
                            'public': True,  # for test download
                        })
                        rec.message_post(
                            body=_("Attachment created successfully."))
                        link_download = \
                            self._get_link_pdf(attachment, download=True)
                        printing_ok.append(rec.id)
                        message.append({
                            'name': rec.system_origin_number,
                            'link_download': link_download,
                            'status': 'OK',
                            'errorMessage': False})
                    else:
                        rec.message_post(body=_("%s" % res['errorMessage']))
                        rec.write({'state': 'exception'})
                        message.append({
                            'name': rec.system_origin_number,
                            'link_download': False,
                            'status': res['status'],
                            'errorMessage': res['errorMessage']})
                except Exception as e:
                    configerror = 'Could not reach configured server'
                    messageerror = 'A error encountered : %s ' % e
                    _logger.error(configerror)
                    _logger.error(messageerror)
                    rec.message_post(
                        body=_("%s %s" % (configerror, messageerror)))
                    rec.write({'state': 'exception'})
                    message.append({
                        'name': rec.system_origin_number,
                        'link_download': False,
                        'status': 'ER',
                        'errorMessage':
                            _('%s %s' % (configerror, messageerror))})

        # Auto post (printed)
        if printing_ok:
            self.browse(printing_ok).action_post()
        print(message)
        print("=======")
        return message
