import os
import re
import subprocess
import frappe
from frappe.model.document import Document


def run_bench_shell_script_realtime(script_path, args=None, event_name="bench_shell_log"):
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


def link_matching_python_and_node(py_ver, n_ver):
	"""Helper to find existing Python Version and Node Version doc names."""
	linked_py = None
	linked_node = None

	if py_ver and py_ver != "Unknown":
		match_py = frappe.db.get_value("Python Version", {"python_version": py_ver}, "name")
		if not match_py:
			match_py = frappe.db.get_value("Python Version", {"name": ["like", f"%{py_ver}%"]}, "name")
		linked_py = match_py

	if n_ver and n_ver != "Unknown":
		match_node = frappe.db.get_value("Node Version", {"node_version": n_ver}, "name")
		if not match_node:
			match_node = frappe.db.get_value("Node Version", {"name": ["like", f"%{n_ver}%"]}, "name")
		linked_node = match_node

	return linked_py, linked_node


def inspect_bench_apps(bench_path):
	"""
	Inspects apps directory inside bench_path and returns list of dicts:
	[{'app_name': 'frappe', 'version': '16.31.0', 'branch': 'version-16'}, ...]
	"""
	apps_dir = os.path.join(bench_path, "apps")
	apps_list = []
	if not os.path.isdir(apps_dir):
		return apps_list

	for app_name in os.listdir(apps_dir):
		app_path = os.path.join(apps_dir, app_name)
		if not os.path.isdir(app_path):
			continue

		# 1. Branch Name
		branch = "Unknown"
		if os.path.isdir(os.path.join(app_path, ".git")):
			try:
				res = subprocess.run(
					["git", "-C", app_path, "rev-parse", "--abbrev-ref", "HEAD"],
					capture_output=True,
					text=True,
					timeout=3
				)
				if res.returncode == 0 and res.stdout.strip():
					branch = res.stdout.strip()
			except Exception:
				pass

		# 2. Version
		version = "Unknown"
		init_file = os.path.join(app_path, app_name, "__init__.py")
		if not os.path.isfile(init_file):
			for root, _, files in os.walk(app_path):
				if "__init__.py" in files:
					candidate = os.path.join(root, "__init__.py")
					try:
						with open(candidate, "r", encoding="utf-8") as f:
							content = f.read()
							match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
							if match:
								version = match.group(1)
								break
					except Exception:
						pass
		else:
			try:
				with open(init_file, "r", encoding="utf-8") as f:
					content = f.read()
					match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
					if match:
						version = match.group(1)
			except Exception:
				pass

		if version == "Unknown" and os.path.isfile(os.path.join(app_path, "pyproject.toml")):
			try:
				with open(os.path.join(app_path, "pyproject.toml"), "r", encoding="utf-8") as f:
					content = f.read()
					match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
					if match:
						version = match.group(1)
			except Exception:
				pass

		apps_list.append({
			"app_name": app_name,
			"version": version,
			"branch": branch
		})

	return apps_list


class Bench(Document):
	def validate(self):
		if not self.bench_name:
			frappe.throw(frappe._("Bench Name is required."))

		b_name = self.bench_name.strip()
		parent_dir = os.path.dirname(self.path) if self.path else os.path.dirname(os.path.abspath(frappe.get_app_path("frappe")))
		target_path = self.path or os.path.join(parent_dir, b_name)

		if not os.path.exists(target_path):
			script_path = os.path.join(frappe.get_app_path("site_manager"), "scripts", "create_bench.sh")
			if not os.path.exists(script_path):
				frappe.throw(frappe._("Shell script not found at {0}").format(script_path))

			f_branch = self.frappe_version or "version-16"
			py_path = ""
			if self.python_version:
				py_path = frappe.db.get_value("Python Version", self.python_version, "path") or ""

			node_ver = self.node_version or ""

			return_code, full_output, result_lines = run_bench_shell_script_realtime(
				script_path, [b_name, f_branch, py_path, node_ver, parent_dir]
			)
			if return_code != 0 or not result_lines:
				frappe.throw(frappe._("Failed to initialize bench {0}: {1}").format(b_name, full_output))

			parts = result_lines[-1].split("|")
			if len(parts) >= 6:
				self.path = parts[1]
				self.frappe_version = parts[2]
				self.status = parts[5]
				if len(parts) >= 7:
					self.bench_version = parts[6]
		else:
			self.path = target_path
			if not self.status:
				self.status = "Stopped"

		# Inspect and populate apps child table
		apps_list = inspect_bench_apps(target_path)
		self.set("apps", [])
		for app_info in apps_list:
			self.append("apps", app_info)


@frappe.whitelist()
def fetch_and_sync_benches():
	"""
	Runs shell script to discover all bench directories and syncs them into Bench DocType.
	"""
	script_path = os.path.join(frappe.get_app_path("site_manager"), "scripts", "fetch_bench_list.sh")
	if not os.path.exists(script_path):
		frappe.throw(frappe._("Shell script not found at {0}").format(script_path))

	search_dir = os.path.expanduser("~")
	return_code, full_output, result_lines = run_bench_shell_script_realtime(script_path, [search_dir])
	if return_code != 0:
		frappe.throw(frappe._("Failed to execute shell script: {0}").format(full_output))

	existing_records = {doc.name: doc for doc in frappe.get_all("Bench", fields=["name", "bench_name", "path", "frappe_version", "python_version", "node_version", "status", "bench_version"])}

	synced = []
	for res_line in result_lines:
		parts = res_line.split("|")
		if len(parts) < 6:
			continue
		b_name, b_path, f_ver, py_ver, n_ver, status = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
		b_ver = parts[6] if len(parts) >= 7 else None

		linked_py, linked_node = link_matching_python_and_node(py_ver, n_ver)
		apps_list = inspect_bench_apps(b_path)

		if b_name in existing_records:
			doc = frappe.get_doc("Bench", b_name)
			updated = False
			if doc.path != b_path:
				doc.path = b_path
				updated = True
			if doc.frappe_version != f_ver:
				doc.frappe_version = f_ver
				updated = True
			if doc.status != status:
				doc.status = status
				updated = True
			if b_ver and doc.bench_version != b_ver:
				doc.bench_version = b_ver
				updated = True
			if linked_py and doc.python_version != linked_py:
				doc.python_version = linked_py
				updated = True
			if linked_node and doc.node_version != linked_node:
				doc.node_version = linked_node
				updated = True

			# Update apps child table
			doc.set("apps", [])
			for app_info in apps_list:
				doc.append("apps", app_info)

			doc.save(ignore_permissions=True)
			synced.append(doc.name)
		else:
			new_doc = frappe.get_doc({
				"doctype": "Bench",
				"bench_name": b_name,
				"path": b_path,
				"frappe_version": f_ver,
				"bench_version": b_ver,
				"python_version": linked_py,
				"node_version": linked_node,
				"status": status,
				"apps": apps_list
			})
			new_doc.insert(ignore_permissions=True)
			synced.append(new_doc.name)

	frappe.db.commit()
	return synced
