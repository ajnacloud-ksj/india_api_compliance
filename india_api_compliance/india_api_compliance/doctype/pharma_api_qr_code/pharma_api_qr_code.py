# Copyright (c) 2023, Ajna Cloud and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import local
import boto3
import json 
import datetime 
import re
from india_api_compliance.utils import get_app_config,extract_fields,get_s3_client


@frappe.whitelist()
def add_tag_to_document(docname, tag):
    tag_doc = frappe.get_doc({
        'doctype': 'Tag Link',
        'tag': tag,
        'document_type': 'Pharma API QR Code',
        'document_name': docname
    })
    tag_doc.insert(ignore_permissions=True)

@frappe.whitelist()
def post_comment_on_document(docname, comment):
    frappe.get_doc({
        'doctype': 'Comment',
        'comment_type': 'Comment',
        'reference_doctype': 'Pharma API QR Code',
        'reference_name': docname,
        'content': comment
    }).insert(ignore_permissions=True)

@frappe.whitelist()
def update_document_status(docname, status):
    # Fetch the document using its name
    doc = frappe.get_doc('Pharma API QR Code', docname)

    # Update the status
    doc.db_set('s3_upload_status', status)
    frappe.db.commit()

@frappe.whitelist()
def capture_and_store_in_s3(qrcodeDocuments, 
                            companyname,
                            docname):
    s3_client = get_s3_client()
    s3Bucket = get_app_config("s3_bucket")
    S3Prefix = get_app_config("s3_prefix")
    print("Paramesh")
    print(f'Paramesh qrcodelist type {type(qrcodeDocuments)}')
    print(qrcodeDocuments)
    docs = json.loads(qrcodeDocuments)
    #docs = qrcodeDocuments
    print(f"length of the array {len(docs)}")

    for doc in docs:
        try: 
            print(f'Paramesh doc type {type(doc)}')
            print(doc)
            sscc_number = doc['container_code']
            s3_key = f"{S3Prefix}/companyname={companyname}/{sscc_number}.json"

            print(f"Paramesh S3 key {s3_key}")

            frappe.logger().info(f"Uploading to S3: {s3_key}")
            res = s3_client.put_object(Body=json.dumps(doc, indent=2), Bucket=s3Bucket, Key=s3_key)
            print(f"Paramesh S3 upoload res {res}")
            update_document_status(docname, "Completed")
            #add_tag_to_document(docname, "S3 Uploaded")
            #post_comment_on_document(docname, "Successfully uploaded to S3.")
        except Exception as e:
            frappe.log_error(f"Failed to upload to S3: {e}", 'S3 Upload Error') 
            update_document_status(docname, "Failed")   


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
        full_sscc_details = []
        site_name = local.site
        qr_code_mandatory_fields_string = get_app_config(key='mandatory_fields')
        qr_code_custom_fields_string = get_app_config(key='custom_fields')
        # Use a default empty string if the value is None before splitting
        # and filter out any empty strings after splitting
        qr_code_mandatory_fields = [field.strip() for field in (qr_code_mandatory_fields_string or '').split(',') if field.strip()]
        qr_code_custom_fields = [field.strip() for field in (qr_code_custom_fields_string or '').split(',') if field.strip()]

        for sscc_detail in self.sscc_details:
            if sscc_detail.net_weight == 0.0:
                frappe.throw(f'Net Weight at index {sscc_detail.idx} could not be zero')
            if sscc_detail.tare_weight == 0.0:
                frappe.throw(f'Tare Weight at index {sscc_detail.idx} could not be zero')
            if sscc_detail.gross_weight == 0.0:
                frappe.throw(f'Gross Weight at index {sscc_detail.idx} could not be zero')
            if sscc_detail.qr_code:
                frappe.delete_doc('File', {'file_url':sscc_detail.qr_code})
                sscc_detail.qr_code = ''
            # Fetch the corresponding Pharma SSCC Item
            pharmaSSCItem = frappe.get_doc("Pharma SSCC Item", sscc_detail.name).as_dict()
            # Combine necessary fields
            combined_data = {
                "container_code": pharmaSSCItem.get('container_code'),
                "net_weight": pharmaSSCItem.get('net_weight'),
                "tare_weight": pharmaSSCItem.get('tare_weight'),
                "gross_weight": pharmaSSCItem.get('gross_weight'),
                "sscc_batch_number": pharmaSSCItem.get('batch_number'),
                "sscc_unit_of_measurement": pharmaSSCItem.get('unit_of_measurement'),
                # Add more fields as needed
            }
            #extract_qr_fields = extract_fields(doc=self, fields= qr_code_mandatory_fields + qr_code_custom_fields)
            extracted_data = extract_fields(doc=self, fields=qr_code_mandatory_fields + qr_code_custom_fields)
            print(extracted_data)
            # Extract the 'sscc_details' and remove it from 'extracted_data'
            sscc_details = extracted_data.pop('sscc_details', None)

            combined_data.update(extracted_data)  
            full_sscc_details.append(combined_data)
        
        frappe.enqueue('india_api_compliance.india_api_compliance.doctype.pharma_api_qr_code.pharma_api_qr_code.capture_and_store_in_s3', 
                        qrcodeDocuments=json.dumps(full_sscc_details, indent=4),
                        companyname=site_name,
                        docname=self.name)              
        # capture_and_store_in_s3(full_sscc_details,site_name,self.name)
        update_document_status(self.name, "Started") 
        frappe.db.commit()


    def on_cancel(self):
        for i in self.sscc_details:
            frappe.db.set_value('Pharma Container Code',i.container_code , {'status': "Not Used"})
            frappe.db.commit()


    