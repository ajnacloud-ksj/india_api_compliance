import frappe
import logging
import pyqrcode
import base64
from io import BytesIO

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
        config = frappe.get_doc("App Configuration", "App Configuration") 
        
        if key:
            return getattr(config, key, None)
        return config
    except frappe.DoesNotExistError:
        return None


