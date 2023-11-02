import frappe
import logging
import pyqrcode
import base64
from io import BytesIO
import boto3

@frappe.whitelist()
def generate_qr_base64(data):
    logging.info(f"Received the data {data}")
    qr = pyqrcode.create(data)
    stream = BytesIO()
    qr.png(stream, scale=5)
    return base64.b64encode(stream.getvalue()).decode()

def get_app_config(key=None):
    try:
        # Assuming there's only one record for App Configuration
        config = frappe.get_doc("QRCode App Configuration", "App Configuration") 
        
        if key:
            return getattr(config, key, None)
        return config
    except frappe.DoesNotExistError:
        return None


def get_s3_client_local():
    s3_client = boto3.client(
        's3',
        aws_access_key_id='your_access_key_id',
        aws_secret_access_key='your_secret_access_key',
        region_name='your_region'
    )
    return s3_client


def extract_fields(doc, fields):
    """Extract the specified fields from the document"""
    data = {field: doc.get(field) for field in fields}
    return data
