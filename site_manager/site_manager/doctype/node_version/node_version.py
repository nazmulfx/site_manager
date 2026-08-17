import os
import subprocess
import frappe
from frappe.model.document import Document


def run_shell_script_realtime(script_path, args=None, event_name="node_version_shell_log"):
	"""
	Runs bash script and streams output lines live via frappe.publish_realtime.
	Returns (return_code, full_output, result_lines)
	"""
	if args is None:
		args = []

	cmd = ["bash", script_path] + [str(a) for a in args]
	user = frappe.session.user if hasattr(frappe, "session") else None

	process = subprocess.Popen(
		cmd,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		text=True,
		bufsize=1
	)

	full_output = []
	result_lines = []

	for line in iter(process.stdout.readline, ""):
		if line:
			full_output.append(line)
			clean_line = line.strip()
			if clean_line.startswith("RESULT:"):
				result_lines.append(clean_line.replace("RESULT:", "").strip())
			elif "|" in clean_line and not clean_line.startswith("Found"):
				result_lines.append(clean_line)

			if user:
				frappe.publish_realtime(
					event=event_name,
					message={"line": line},
					user=user
				)

	process.stdout.close()
	return_code = process.wait()
	return return_code, "".join(full_output), result_lines


class NodeVersion(Document):
	def validate(self):
		if not self.node_version:
			frappe.throw(frappe._("Node Version is required."))

		ver = self.node_version.strip()
		is_def_str = "1" if self.is_default else "0"

		script_path = os.path.join(frappe.get_app_path("site_manager"), "scripts", "install_node_version.sh")
		if not os.path.exists(script_path):
			frappe.throw(frappe._("Shell script not found at {0}").format(script_path))

		return_code, full_output, result_lines = run_shell_script_realtime(script_path, [ver, is_def_str])
		if return_code != 0 or not result_lines:
			frappe.throw(frappe._("Failed to install Node version {0}: {1}").format(ver, full_output))

		parts = result_lines[-1].split("|")
		if len(parts) >= 2:
			self.installed_node_version = parts[0]
			self.path = parts[1]
		else:
			frappe.throw(frappe._("Invalid response from install script: {0}").format(full_output))

	def on_update(self):
		if self.is_default:
			script_path = os.path.join(frappe.get_app_path("site_manager"), "scripts", "set_default_node_version.sh")
			if os.path.exists(script_path):
				target_ver = self.installed_node_version or self.node_version
				run_shell_script_realtime(script_path, [target_ver])
			frappe.db.sql("UPDATE `tabNode Version` SET is_default = 0 WHERE name != %s", self.name)


@frappe.whitelist()
def fetch_and_sync_node_versions():
	"""
	Runs shell script to fetch all installed Node.js versions and syncs them into Node Version DocType.
	"""
	script_path = os.path.join(frappe.get_app_path("site_manager"), "scripts", "fetch_node_versions.sh")
	if not os.path.exists(script_path):
		frappe.throw(frappe._("Shell script not found at {0}").format(script_path))

	return_code, full_output, result_lines = run_shell_script_realtime(script_path)
	if return_code != 0:
		frappe.throw(frappe._("Failed to execute shell script: {0}").format(full_output))

	existing_records = {doc.name: doc for doc in frappe.get_all("Node Version", fields=["name", "node_version", "is_default", "path"])}

	synced = []
	for res_line in result_lines:
		parts = res_line.split("|")
		if len(parts) < 3:
			continue
		ver, bin_path, is_def_str = parts[0], parts[1], parts[2]
		is_def = 1 if is_def_str == "1" else 0

		if ver in existing_records:
			doc = frappe.get_doc("Node Version", ver)
			updated = False
			if doc.is_default != is_def:
				doc.is_default = is_def
				updated = True
			if doc.path != bin_path:
				doc.path = bin_path
				updated = True
			if doc.installed_node_version != ver:
				doc.installed_node_version = ver
				updated = True
			if updated:
				doc.save(ignore_permissions=True)
			synced.append(doc.name)
		else:
			new_doc = frappe.get_doc({
				"doctype": "Node Version",
				"node_version": ver,
				"installed_node_version": ver,
				"is_default": is_def,
				"path": bin_path
			})
			new_doc.insert(ignore_permissions=True)
			synced.append(new_doc.name)

	frappe.db.commit()
	return synced


