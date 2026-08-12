import os
import re
import shutil
import subprocess
import glob
import frappe
from frappe import _

@frappe.whitelist()
def get_system_info():
	"""
	Returns installed Python binaries, Node version, Git version, and default paths.
	"""
	pythons = []
	seen = set()

	# Search common python binary paths
	possible_paths = [
		"/usr/bin/python3*",
		"/usr/local/bin/python3*",
		os.path.expanduser("~/.pyenv/shims/python3*"),
		os.path.expanduser("~/.local/bin/python3*")
	]

	for pattern in possible_paths:
		for p in glob.glob(pattern):
			if os.path.isfile(p) and os.access(p, os.X_OK):
				real_p = os.path.realpath(p)
				if real_p in seen:
					continue
				seen.add(real_p)
				try:
					res = subprocess.run([p, "--version"], capture_output=True, text=True, timeout=2)
					ver_str = res.stdout.strip() or res.stderr.strip()
					if ver_str.startswith("Python"):
						pythons.append({"path": p, "version": ver_str})
				except Exception:
					pass

	# Add default python3 fallback if empty
	if not pythons:
		pythons.append({"path": "python3", "version": "Python 3 (System Default)"})

	# Get Node version
	node_ver = "Unknown"
	try:
		node_res = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=2)
		node_ver = node_res.stdout.strip()
	except Exception:
		pass

	# Get Current Bench Path
	current_bench = os.path.abspath(os.path.join(frappe.get_app_path("frappe"), "..", ".."))

	return {
		"python_executables": pythons,
		"node_version": node_ver,
		"current_bench": current_bench,
		"default_parent_dir": os.path.dirname(current_bench)
	}

@frappe.whitelist()
def get_benches(search_dir=None):
	"""
	Scans directory for valid Frappe bench folders.
	"""
	if not search_dir:
		current_bench = os.path.abspath(os.path.join(frappe.get_app_path("frappe"), "..", ".."))
		search_dir = os.path.dirname(current_bench)

	benches = []
	if not os.path.exists(search_dir):
		return benches

	for item in os.listdir(search_dir):
		full_path = os.path.join(search_dir, item)
		if os.path.isdir(full_path) and is_valid_bench(full_path):
			bench_info = inspect_bench(full_path)
			benches.append(bench_info)

	return benches

def is_valid_bench(path):
	"""Checks if a directory has apps/frappe and sites/"""
	has_sites = os.path.isdir(os.path.join(path, "sites"))
	has_frappe = os.path.isdir(os.path.join(path, "apps", "frappe"))
	return has_sites and has_frappe

def inspect_bench(path):
	bench_name = os.path.basename(path)

	# Get Frappe Version
	frappe_init = os.path.join(path, "apps", "frappe", "frappe", "__init__.py")
	frappe_version = "Unknown"
	if os.path.isfile(frappe_init):
		try:
			with open(frappe_init, "r", encoding="utf-8") as f:
				content = f.read()
				match = re.search(r'__version__\s*=\*?\s*["\']([^"\']+)["\']', content)
				if match:
					frappe_version = match.group(1)
		except Exception:
			pass

	# Get Python Version
	python_env = os.path.join(path, "env", "bin", "python")
	python_version = "Unknown"
	if os.path.isfile(python_env):
		try:
			res = subprocess.run([python_env, "--version"], capture_output=True, text=True, timeout=2)
			python_version = res.stdout.strip() or res.stderr.strip()
		except Exception:
			pass

	# Get Sites List
	sites_dir = os.path.join(path, "sites")
	sites = []
	if os.path.isdir(sites_dir):
		for item in os.listdir(sites_dir):
			item_path = os.path.join(sites_dir, item)
			if os.path.isdir(item_path) and not item.startswith(".") and item not in ["assets", "languages"]:
				if os.path.isfile(os.path.join(item_path, "site_config.json")):
					sites.append(item)

	# Check process status
	status = "Stopped"
	try:
		# Check if Procfile or redis/web is active or if PID exists
		res = subprocess.run(["pgrep", "-f", f"frappe.*{bench_name}"], capture_output=True, text=True)
		if res.returncode == 0 and res.stdout.strip():
			status = "Running"
	except Exception:
		pass

	return {
		"name": bench_name,
		"path": path,
		"frappe_version": frappe_version,
		"python_version": python_version,
		"sites_count": len(sites),
		"sites": sites,
		"status": status
	}

@frappe.whitelist()
def get_bench_details(bench_path):
	"""
	Returns detailed info for a specific bench path.
	"""
	if not os.path.exists(bench_path) or not is_valid_bench(bench_path):
		frappe.throw(_("Invalid bench directory path: {0}").format(bench_path))

	summary = inspect_bench(bench_path)

	# Get installed apps
	apps_dir = os.path.join(bench_path, "apps")
	apps = []
	if os.path.isdir(apps_dir):
		for item in os.listdir(apps_dir):
			app_path = os.path.join(apps_dir, item)
			if os.path.isdir(app_path) and not item.startswith("."):
				# Git branch
				git_branch = "Unknown"
				try:
					res = subprocess.run(["git", "-C", app_path, "branch", "--show-current"], capture_output=True, text=True)
					git_branch = res.stdout.strip() or "HEAD"
				except Exception:
					pass

				apps.append({
					"name": item,
					"path": app_path,
					"branch": git_branch
				})

	# Get Sites details
	sites_dir = os.path.join(bench_path, "sites")
	sites_detailed = []
	for s_name in summary["sites"]:
		site_config_path = os.path.join(sites_dir, s_name, "site_config.json")
		db_name = "N/A"
		if os.path.isfile(site_config_path):
			try:
				cfg = frappe.parse_json(open(site_config_path).read())
				db_name = cfg.get("db_name", "N/A")
			except Exception:
				pass
		sites_detailed.append({
			"name": s_name,
			"db_name": db_name,
			"path": os.path.join(sites_dir, s_name)
		})

	summary["apps_list"] = apps
	summary["sites_detailed"] = sites_detailed
	return summary

@frappe.whitelist()
def create_bench(bench_name, frappe_branch="version-16", python_path="python3", apps=None, parent_dir=None):
	"""
	Initializes a new bench folder asynchronously.
	"""
	if not bench_name:
		frappe.throw(_("Bench name is required"))

	if not parent_dir:
		current_bench = os.path.abspath(os.path.join(frappe.get_app_path("frappe"), "..", ".."))
		parent_dir = os.path.dirname(current_bench)

	target_path = os.path.join(parent_dir, bench_name)
	if os.path.exists(target_path):
		frappe.throw(_("Directory already exists at {0}").format(target_path))

	# Construct bench init command
	cmd = [
		"bench", "init",
		"--frappe-branch", frappe_branch,
		"--python", python_path,
		target_path
	]

	try:
		# Run bench init command
		process = subprocess.Popen(
			cmd,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			text=True,
			cwd=parent_dir
		)

		return {
			"status": "success",
			"message": f"Bench creation started for {bench_name} at {target_path}",
			"target_path": target_path
		}
	except Exception as e:
		frappe.throw(_("Failed to start bench init: {0}").format(str(e)))

@frappe.whitelist()
def create_site(bench_path, site_name, admin_password="admin"):
	"""
	Creates a new site inside the target bench.
	"""
	if not os.path.exists(bench_path) or not is_valid_bench(bench_path):
		frappe.throw(_("Invalid bench path"))

	cmd = [
		"bench", "--site", site_name, "new-site",
		"--admin-password", admin_password,
		"--no-mariadb-socket"
	]

	try:
		res = subprocess.run(cmd, cwd=bench_path, capture_output=True, text=True, timeout=120)
		if res.returncode == 0:
			return {"status": "success", "message": f"Site {site_name} created successfully"}
		else:
			frappe.throw(_("Error creating site: {0}").format(res.stderr or res.stdout))
	except Exception as e:
		frappe.throw(_("Site creation failed: {0}").format(str(e)))
