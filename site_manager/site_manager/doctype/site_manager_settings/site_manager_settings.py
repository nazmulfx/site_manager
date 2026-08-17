import frappe
from frappe.model.document import Document
from site_manager.site_manager.doctype.node_version.node_version import fetch_and_sync_node_versions
from site_manager.site_manager.doctype.python_version.python_version import fetch_and_sync_python_versions
from site_manager.site_manager.doctype.bench.bench import fetch_and_sync_benches


class SiteManagerSettings(Document):
	@frappe.whitelist()
	def fetch_node_version(self):
		return fetch_and_sync_node_versions()

	@frappe.whitelist()
	def fetch_python_version(self):
		return fetch_and_sync_python_versions()

	@frappe.whitelist()
	def fetch_bench_list(self):
		return fetch_and_sync_benches()
