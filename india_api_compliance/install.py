import frappe
import logging
# Set up a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set this to the desired level

# Ensure Frappe has been set up to log, or add a handler
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


roles = ["QA User", "QA Reviewer", "QA Approver"]


def after_install():
    # Create roles and set permissions
    create_roles()
    set_permissions()

def create_roles():
    for role_name in roles:
        if not frappe.db.exists('Role', role_name):
            frappe.get_doc({
                'doctype': 'Role',
                'role_name': role_name,
                'desk_access': 1
            }).insert()

def set_permissions():
    doctype = 'Pharma API QR Code'

    # Example permissions, adjust as required
   # For QA User
    frappe.permissions.add_permission(doctype, 'QA User', ptype='read')
    frappe.permissions.add_permission(doctype, 'QA User', ptype='write')

    # For QA Reviewer
    frappe.permissions.add_permission(doctype, 'QA Reviewer', ptype='read')
    frappe.permissions.add_permission(doctype, 'QA Reviewer', ptype='write')

    # For QA Approver
    frappe.permissions.add_permission(doctype, 'QA Approver', ptype='read')
    frappe.permissions.add_permission(doctype, 'QA Approver', ptype='write')
    frappe.permissions.add_permission(doctype, 'QA Approver', ptype='submit')


def before_uninstall():
    # Cleanup roles and permissions
    #remove_permissions()
    remove_roles()


def remove_roles():
    roles = ["QA User", "QA Reviewer", "QA Approver"]
    
    for role_name in roles:
        if frappe.db.exists('Role', role_name):
            frappe.delete_doc('Role', role_name)
