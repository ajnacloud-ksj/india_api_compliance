# Copyright (c) 2023, Ajna Cloud and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import local
import pyqrcode
import png
import sys, os,shutil

from india_api_compliance.utils import get_app_config

api_url = get_app_config("client_api_url")


class PharmaAPIQRCode(Document):
    def validate(self):
        if int(self.number_of_containers) >= 500:
            frappe.throw('Container Code should be less then 500')
        dd = 0
        for i in range(0,int(self.number_of_containers)):
            try:
                cu = self.sscc_details[dd]
                if not cu.container_code:
                    frappe.msgprint(f'no container {cu}')
                    cc =frappe.get_doc({'doctype': 'Pharma Container Code'})
                    cc.status = 'Used'
                    cc.unit_value =self.unit_value
                    cc.save()
                    frappe.db.commit()
                    cu.container_code = cc.name
                cu.gross_weight = cu.net_weight + cu.tare_weight
            except IndexError:
                row=self.append('sscc_details',{})
                cc =frappe.get_doc({'doctype': 'Pharma Container Code'})
                cc.status = 'Used'
                cc.unit_value =self.unit_value
                cc.save()
                frappe.db.commit()
                row.container_code = cc.name
            dd= dd +1

        if self.date_of_expiry_or_retest < self.date_of_manufacturing:
            frappe.throw('Date of Expiration should not be less than Date of Manufacturing')

            
    def on_submit(self):
        for i in self.sscc_details:
            if i.net_weight == 0.0:
                frappe.throw(f'Net Weight at index {i.idx} could not be zero')
            if i.tare_weight == 0.0:
                frappe.throw(f'Tare Weight at index {i.idx} could not be zero')
            if i.gross_weight == 0.0:
                frappe.throw(f'Gross Weight at index {i.idx} could not be zero')
            if i.qr_code:
                frappe.delete_doc('File', {'file_url':i.qr_code})
                i.qr_code = ''

            fname = f"{self.product_code}{i.name}".replace("#","").replace("/","").replace(" ","")
            import re

            site_name = local.site


            url = pyqrcode.create(f'https://i2mcdf76y2.execute-api.ap-south-1.amazonaws.com/dev/ajnaerpsearchapi?id={self.name}&site_name={site_name}&sscc={i.container_code}')

            cwd = os.getcwd()
            url.png(f'{fname}.png', scale = 6)
            src_path = os.path.join(cwd,  f'{fname}.png')
            dst_path = os.path.join(frappe.get_site_path()+'/public/files/', f'{fname}.png')
            shutil.move(src_path, dst_path)
            doc=frappe.new_doc('File')
            doc.file_url=f'/files/{fname}.png'
            doc.is_private=0
            doc.file_size=os.path.getsize(f"{frappe.get_site_path()}/public/files/{fname}.png")
            doc.save()
            frappe.db.set_value(i.doctype,i.name,{"qr_code":doc.file_url})
            i.qr_code = doc.file_url
            frappe.db.commit()

    def on_cancel(self):
        for i in self.sscc_details:
            frappe.db.set_value('Pharma Container Code',i.container_code , {'status': "Not Used"})
            frappe.db.commit()
