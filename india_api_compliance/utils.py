import frappe
import logging
import pyqrcode
import base64
from io import BytesIO
import boto3
import json 
from frappe.exceptions import DoesNotExistError

@frappe.whitelist()
def generate_qr_base64(data):
    logging.info(f"Received the data {data}")
    qr = pyqrcode.create(data)
    stream = BytesIO()
    qr.png(stream, scale=5)
    return base64.b64encode(stream.getvalue()).decode()

def get_app_config(key=None):
    try:
        # Fetching the Singleton Doctype
        config = frappe.get_doc("India Api Compliance Configuration")
        # If the requested key is the secret key, decrypt it
        if key == 's3_secret_key':
            return config.get_password(fieldname=key)
        # For other keys, return the attribute value
        elif key:
            return getattr(config, key, None)
        # If no key is specified, return the whole config
        return config
    except frappe.exceptions.DoesNotExistError:
        # Return None if the Doctype does not exist
        return None


def get_s3_client():
    useS3AccessKeys= get_app_config("use_access_keys")
    if useS3AccessKeys:
        print("Using S3 access keys to initialize the S3 client")
        return get_s3_client_using_access_keys()
    else: 
        return boto3.client('s3')
               

def get_s3_client_using_access_keys():
    access_key = get_app_config("s3_access_key")
    print(f"AWS Key: {access_key}")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=get_app_config("s3_access_key"),
        aws_secret_access_key=get_app_config("s3_secret_key"),
        region_name='ap-south-1'
    )
    return s3_client


def serialize_custom_object(custom_object):
    # Implement this function to convert your custom objects to a serializable format.
    # For example:
        return {
            'id': custom_object.id,
            'docstatus': custom_object.docstatus,
            'parent': custom_object.parent
        }
'''
def extract_fields(doc, fields):
        """Extract the specified fields from the document"""
        data = {}
        for field in fields:
            value = doc.get(field)
            # Check if value is a list and if items in the list are custom objects
            if isinstance(value, list) and value and hasattr(value[0], 'docstatus'):
                # Convert each custom object to a dict
                value = [serialize_custom_object(item) for item in value]
            data[field] = value
        return data    

'''

def extract_fields(doc, fields):
    """Extract the specified fields from the document"""
    data = {field: doc.get(field) for field in fields}
    return data

