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

def remove_custom_print_formats():
    # Define a list of print formats that need to be removed
    print_formats_to_remove = ["API QRCode STD"]  # Add your print format names here

    for pf in print_formats_to_remove:
        # Check if the print format exists
        if frappe.db.exists("Print Format", pf):
            # Delete the print format
            frappe.delete_doc("Print Format", pf)



def after_install():
    # Create roles and set permissions
    create_roles()
    #set_permissions()

def create_roles():
    for role_name in roles:
        if not frappe.db.exists('Role', role_name):
            frappe.get_doc({
                'doctype': 'Role',
                'role_name': role_name,
                'desk_access': 1
            }).insert()

def remove_custom_workspace(workspace_name):
    # Check if the workspace exists
    if frappe.db.exists('Workspace', workspace_name):
        # Get the document
        workspace_doc = frappe.get_doc('Workspace', workspace_name)

        # Delete the workspace
        workspace_doc.delete()
    frappe.db.commit()

def before_uninstall():
    # Cleanup roles and permissions
    #remove_permissions()
    #remove_roles()
    remove_custom_workspace('India Compliance')
    remove_custom_print_formats()


def remove_roles():
    roles = ["QA User", "QA Reviewer", "QA Approver"]
    
    for role_name in roles:
        if frappe.db.exists('Role', role_name):
            frappe.delete_doc('Role', role_name)
