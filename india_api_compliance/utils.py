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
        # Printing the entire config as JSON
        print(json.dumps(config.as_dict()))
        print("Fetching the config")
        # If a specific key is requested, return its value
        print(f"Looking for key {key}")
        if key:
            return getattr(config, key, None)
        # If no key is specified, return the whole config
        return config
    except DoesNotExistError:
        # Return None if the Doctype does not exist
        return None


def get_s3_client_using_access_keys():
    s3_client = boto3.client(
        's3',
        aws_access_key_id=get_app_config("s3_access_key"),
        aws_secret_access_key=get_app_config("s3_secret_key"),
        region_name='ap-south-1'
    )
    return s3_client


def extract_fields(doc, fields):
    """Extract the specified fields from the document"""
    data = {field: doc.get(field) for field in fields}
    return data
