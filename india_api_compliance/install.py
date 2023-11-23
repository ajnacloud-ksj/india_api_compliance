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


def create_workflow_action_master():
    doc = frappe.get_doc({
        'doctype': 'Workflow Action Master',
        'name': 'Cancel',
        'owner': 'Administrator',
        'workflow_action_name': 'Cancel'
        'docstatus': 0
    })
    doc.insert()

def create_workflow_state():
    doc = frappe.get_doc({
        'doctype': 'Workflow State',
        'name': 'Cancelled',
        'owner': 'Administrator',
        'docstatus': 0
    })
    doc.insert()

def remove_custom_print_formats():
    # Define a list of print formats that need to be removed
    print_formats_to_remove = ["API QRCode STD"]  # Add your print format names here

    for pf in print_formats_to_remove:
        # Check if the print format exists
        if frappe.db.exists("Print Format", pf):
            # Delete the print format
            frappe.delete_doc("Print Format", pf)

def get_custom_blocks():
  blocks = [
        {
            'doctype': 'Custom HTML Block',
            'name': 'App Header',
            "html": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>India Compliance</title>\n    <link rel=\"stylesheet\" href=\"style.css\">\n</head>\n<body>\n\n    <header class=\"app-header\">\n        <h1 class=\"app-title\">India Compliance</h1>\n    </header>\n</body>\n</html>\n",
            "script": "document.addEventListener(\"DOMContentLoaded\", function() {\n    const iconsContainer = document.querySelector('.animated-icons');\n    \n    // Initial delay before the animation starts\n    setTimeout(() => {\n        iconsContainer.style.opacity = 1; // Make icons appear\n    }, 500);\n\n    // Delay for icons to disappear\n    setTimeout(() => {\n        iconsContainer.style.opacity = 0; // Make icons disappear\n    }, 3000); // Adjust the timing as needed\n});\n",
            "style": "body {\n    margin: 0;\n    padding: 0;\n    font-family: 'Roboto', sans-serif; /* Update the font family */\n    background-color: #f4f4f4;\n    color: #333;\n}\n\n.app-header {\n    background-color: #005f73;\n    padding: 20px;\n    text-align: center;\n    border-radius: 10px; /* Rounded corners */\n    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); /* Box shadow for depth */\n}\n\n.app-title {\n    margin: 0;\n    color: white;\n    font-size: 2.5em;\n    font-weight: 700; /* Making the title bold */\n}\n\n.animated-icons {\n    font-size: 2em;\n    opacity: 0;\n    transition: opacity 2s ease-in-out;\n    margin-top: 10px;\n    display: flex;\n    justify-content: center;\n    gap: 15px; /* Space between icons */\n}\n\n\n.animated-icons span {\n    animation: bounce 1s infinite alternate;\n    -webkit-animation: bounce 1s infinite alternate;\n}\n\n@keyframes bounce {\n    from { transform: translateY(0); }\n    to { transform: translateY(-20px); }\n}\n\n@media (max-width: 600px) {\n    .app-title {\n        font-size: 1.8em;\n    }\n    .animated-icons {\n        font-size: 1.5em;\n    }\n}\n"
        },
        {
            'doctype': 'Custom HTML Block',
             "name": "Line with Animation",
            "html": "<!DOCTYPE html>\n<html lang=\"en\">\n<body>\n<div class=\"dotted-line\">\n    <div class=\"spark\"></div> <!-- Spark element -->\n</div>\n</body>\n</html>\n",
            "script": "const spark = document.querySelector('.spark');\n\nspark.addEventListener('animationiteration', () => {\n    // Create a random sparkling effect on each iteration\n    const scale = 1 + Math.random() * 0.4;\n    const duration = 0.3 + Math.random() * 0.7;\n    spark.style.animation = `moveSpark 4s infinite, sparkle ${duration}s`;\n\n    const keyframes = `\n        @keyframes sparkle {\n            50% {\n                transform: scale(${scale});\n                box-shadow: 0 0 20px 5px #2BB4D4;\n            }\n        }\n    `;\n\n    // Add the sparkle effect to the style of the document\n    document.styleSheets[0].insertRule(keyframes, 0);\n});\n",
            "style": ".dotted-line {\n    position: relative;\n    border-bottom: 1px dotted #2BB4D4;\n    width: 100%;\n    height: 0;\n}\n\n.spark {\n    position: absolute;\n    left: 0;\n    top: -4px;\n    width: 6px;\n    height: 6px;\n    background-color: white;\n    border-radius: 50%;\n    box-shadow: 0 0 8px 2px #2BB4D4;\n    animation: moveSpark 4s, fadeOutStar 0.5s 4s forwards;  /* Two animations: move and then fade out */\n}\n\n@keyframes moveSpark {\n    0% {\n        left: 0;\n    }\n    100% {\n        left: calc(100% - 6px);\n    }\n}\n\n@keyframes fadeOutStar {\n    0% {\n        transform: scale(1);\n        opacity: 1;\n        box-shadow: 0 0 8px 2px #2BB4D4;\n    }\n    50% {\n        transform: scale(1.5);  /* Burst effect */\n        box-shadow: 0 0 15px 5px #2BB4D4;  /* Increase glow */\n    }\n    100% {\n        opacity: 0;  /* Disappear */\n    }\n}\n"
        }
        # Add more blocks as needed
    ]
  return blocks

def remove_custom_html_blocks():
    # Titles of your Custom HTML Blocks to be removed
    blocks = get_custom_blocks()
    for block in blocks:
        if frappe.db.exists('Custom HTML Block', block['name']):
            doc = frappe.get_doc('Custom HTML Block', block['name'])
            doc.delete()
    frappe.db.commit()

def delete_workflow_action_master():
    frappe.delete_doc('Workflow Action Master', 'Cancel', ignore_missing=True)

def delete_workflow_state():
    frappe.delete_doc('Workflow State', 'Cancelled', ignore_missing=True)

def create_custom_html_blocks():
    # Example data for Custom HTML Block

    blocks = get_custom_blocks()
    for block in blocks:
        if not frappe.db.exists('Custom HTML Block', block['name']):
            doc = frappe.get_doc(block)
            doc.insert()

    frappe.db.commit()


def after_install():
    # Create roles and set permissions
    create_roles()
    create_custom_html_blocks()
    create_workflow_action_master()
    create_workflow_state()
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
    remove_custom_html_blocks()
    delete_workflow_action_master()
    delete_workflow_state()

def remove_roles():
    roles = ["QA User", "QA Reviewer", "QA Approver"]
    
    for role_name in roles:
        if frappe.db.exists('Role', role_name):
            frappe.delete_doc('Role', role_name)
