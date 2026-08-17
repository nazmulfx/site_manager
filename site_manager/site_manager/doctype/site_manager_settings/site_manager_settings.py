import frappe
from frappe.model.document import Document
from site_manager.site_manager.doctype.node_version.node_version import fetch_and_sync_node_versions


class SiteManagerSettings(Document):
	@frappe.whitelist()
	def fetch_node_version(self):
		return fetch_and_sync_node_versions()

