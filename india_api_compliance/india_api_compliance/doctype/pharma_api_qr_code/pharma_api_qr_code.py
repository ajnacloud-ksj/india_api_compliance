# Copyright (c) 2023, Ajna Cloud and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import local
import boto3
import json 
import datetime 
from india_api_compliance.utils import get_app_config,extract_fields,get_s3_client


def capture_and_store_in_s3_old(qrcodeDocument,
                            companyname,
                            sscc_number,
                            s3_client):
    
    s3Bucket = get_app_config("s3_bucket")
    S3Prefix = get_app_config("s3_prefix")
    s3_key = f"{S3Prefix}/{companyname}/{sscc_number}.json"
    print(f"System time: {datetime.datetime.now()}")

    # Convert the JSON object to a string
    json_string = json.dumps(qrcodeDocument, separators=(',', ':'))

    print(json_string)
    print(f"s3_key: {s3_key}, bucket : {s3Bucket} with data: {json_string}")

    # Upload the JSON string as a file-like object
    s3_client.put_object(Body=json_string, Bucket=s3Bucket, Key=s3_key)

class PharmaAPIQRCode(Document):

    def validate_container_count(self):
        if int(self.number_of_containers) >= 500:
            frappe.throw(_('Container Code should be less than 500'))

    def validate_dates(self):
        if self.date_of_expiry_or_retest < self.date_of_manufacturing:
            frappe.throw(_('Date of Expiration should not be less than Date of Manufacturing'))

    def process_container_codes(self):
        # Pre-fetch unit value and unused container codes to minimize database queries
        unit_value = self.unit_value
        unused_container_codes = self.get_unused_container_codes(int(self.number_of_containers))

        for idx, container_detail in enumerate(self.get_container_details()):
            container_code = unused_container_codes[idx]
            self.set_container_code(container_detail, container_code, unit_value)

        # Update database in a single transaction for performance and atomicity
        self.bulk_update_container_codes(unused_container_codes)

    def get_container_details(self):
        # Ensure there's a container detail object for each required container
        while len(self.sscc_details) < int(self.number_of_containers):
            self.append('sscc_details', {})
        return self.sscc_details

    def get_unused_container_codes(self, count):
        # Fetch unused container codes in bulk for efficiency
        return frappe.get_list('Pharma Container Code', 
                               filters={'status': 'Not Used'}, 
                               fields=['name'],
                               limit=count)

    def set_container_code(self, container_detail, container_code, unit_value):
        # Assign container code and calculate gross weight
        if not container_detail.container_code:
            container_detail.container_code = container_code['name']
        container_detail.gross_weight = container_detail.net_weight + container_detail.tare_weight
        # Flag container code as used
        container_code['status'] = 'Used'
        container_code['unit_value'] = unit_value

    def bulk_update_container_codes(self, unused_container_codes):
        # Perform a bulk update to commit changes to all container codes
        names = [code['name'] for code in unused_container_codes]
        frappe.db.sql("""UPDATE `tabPharma Container Code` SET status = 'Used', unit_value = %s 
                         WHERE name IN (%s)""", (self.unit_value, ', '.join(['%s'] * len(names))), tuple(names))
  
    def validate_weights(item):
        if item.net_weight == 0.0:
            frappe.throw(f'Net Weight at index {item.idx} cannot be zero')
        if item.tare_weight == 0.0:
            frappe.throw(f'Tare Weight at index {item.idx} cannot be zero')
        if item.gross_weight == 0.0:
            frappe.throw(f'Gross Weight at index {item.idx} cannot be zero')

    def clear_qr_code_field(item):
        if item.qr_code:
            frappe.delete_doc('File', {'file_url': item.qr_code})
            item.qr_code = ''

    def get_qr_code_fields():
        qr_code_mandatory_fields_string = get_app_config(key='mandatory_fields')
        qr_code_custom_fields_string = get_app_config(key='custom_fields')
        
        qr_code_mandatory_fields = [field.strip() for field in (qr_code_mandatory_fields_string or '').split(',') if field.strip()]
        qr_code_custom_fields = [field.strip() for field in (qr_code_custom_fields_string or '').split(',') if field.strip()]
        
        return qr_code_mandatory_fields, qr_code_custom_fields

    def extract_full_sscc_details(doc, extracted_data):
        sscc_details = extracted_data.pop('sscc_details', None)
        full_sscc_details = []
        
        if sscc_details:
            for sscc_item in sscc_details:
                pharmaSSCItem = frappe.get_doc("Pharma SSCC Item", sscc_item.name).as_dict()
                data = pharmaSSCItem.copy()
                data.update(extracted_data)  
                full_sscc_details.append(data)
        else:
            frappe.log_error("No SSCC details found.", 'SSCC Extraction Error')

        return full_sscc_details

    @frappe.whitelist()
    def capture_and_store_in_s3(qrcodeDocument, companyname, sscc_number, s3_client):
        s3Bucket = get_app_config("s3_bucket")
        S3Prefix = get_app_config("s3_prefix")
        s3_key = f"{S3Prefix}/{companyname}/{sscc_number}.json"

        frappe.logger().info(f"Uploading to S3: {s3_key}")

        try:
            s3_client.put_object(Body=qrcodeDocument, Bucket=s3Bucket, Key=s3_key)
        except Exception as e:
            frappe.log_error(f"Failed to upload to S3: {e}", 'S3 Upload Error')


    def validate(self):
        self.validate_container_count()
        self.validate_dates()
        self.process_container_codes()

    def on_submit(self):
        s3client = get_s3_client()
        for i in self.sscc_details:
           self.validate_weights(i)
           self.clear_qr_code_field(i)

        site_name = frappe.local.site
        qr_code_mandatory_fields, qr_code_custom_fields = self.get_qr_code_fields()

        extracted_data = extract_fields(doc=self, fields=qr_code_mandatory_fields)

        full_sscc_details = self.extract_full_sscc_details(self, extracted_data)
        
        for data in full_sscc_details:
            frappe.enqueue('india_api_compliance.india_api_compliance.doctype.pharma_api_qr_code.capture_and_store_in_s3', 
                        qrcodeDocument=json.dumps(data, indent=4),
                        companyname=site_name,
                        sscc_number=data['container_code'],
                        s3_client=s3client)

        frappe.db.commit()


    def on_cancel(self):
        for i in self.sscc_details:
            frappe.db.set_value('Pharma Container Code',i.container_code , {'status': "Not Used"})
            frappe.db.commit()


    