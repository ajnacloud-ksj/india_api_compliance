# Copyright (c) 2023, Ajna Cloud and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class IndiaApiComplianceConfiguration(Document):

	def on_save(self):
		print("Configuration saved successfully...")
