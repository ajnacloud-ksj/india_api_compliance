# Copyright (c) 2023, Ajna Cloud and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import local
import boto3
import json 

from india_api_compliance.utils import get_app_config,extract_fields,get_s3_client_using_access_keys


def get_s3_client():
    useS3AccessKeys= get_app_config("use_access_keys")
    if not useS3AccessKeys:
        print("Using S3 access keys to initialize the S3 client")
        return get_s3_client_using_access_keys()
    else: 
        return boto3.client('s3')
               

def capture_and_store_in_s3(qrcodeDocument,companyname):

    s3Bucket = get_app_config("s3_bucket")
    S3Prefix = get_app_config("s3_prefix")
    sscc_number = qrcodeDocument['sscc_number']
    s3_key = f"{S3Prefix}/{companyname}/{sscc_number}.json"

    s3_client = get_s3_client()

    # Convert the JSON object to a string
    json_string = json.dumps(qrcodeDocument)

    
    # Upload the JSON string as a file-like object
    s3_client.put_object(Body=json_string, Bucket=s3Bucket, Key=s3_key)

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

            qr_code_mandatory_fields_string = get_app_config(key='mandatory_fields')
            qr_code_custom_fields_string = get_app_config(key='custom_fields')

            # Use a default empty string if the value is None before splitting
            # and filter out any empty strings after splitting
            qr_code_mandatory_fields = [field.strip() for field in (qr_code_mandatory_fields_string or '').split(',') if field.strip()]
            qr_code_custom_fields = [field.strip() for field in (qr_code_custom_fields_string or '').split(',') if field.strip()]


            extract_qr_fields = extract_fields(doc=self, fields= qr_code_mandatory_fields + qr_code_custom_fields)
            
            print(extract_qr_fields)
            capture_and_store_in_s3(qrcodeDocument=extract_qr_fields, companyname=site_name)
            frappe.db.commit()

    def on_cancel(self):
        for i in self.sscc_details:
            frappe.db.set_value('Pharma Container Code',i.container_code , {'status': "Not Used"})
            frappe.db.commit()
