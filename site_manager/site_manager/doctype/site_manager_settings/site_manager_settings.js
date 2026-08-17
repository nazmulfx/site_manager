frappe.ui.form.on("Site Manager Settings", {
	fetch_node_version(frm) {
		const event_name = "node_version_shell_log";

		const d = new frappe.ui.Dialog({
			title: __("Live Shell Output - Fetch Node Versions"),
			size: "large",
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "terminal_html"
				}
			],
			primary_action_label: __("Close"),
			primary_action() {
				frappe.realtime.off(event_name);
				d.hide();
			}
		});

		d.show();

		d.$wrapper.find(".modal-dialog").css({
			"max-width": "920px",
			"width": "90%"
		});

		const $wrapper = d.get_field("terminal_html").$wrapper;
		$wrapper.html(`
			<div style="background: #121212; border-radius: 8px; border: 1px solid #2a2a2a; overflow: hidden;">
				<div style="background: #1e1e1e; padding: 8px 15px; border-bottom: 1px solid #2a2a2a; display: flex; align-items: center; justify-content: space-between;">
					<span style="color: #aaa; font-size: 12px; font-family: monospace;">bash &bull; fetch_node_versions.sh</span>
					<span style="display: inline-block; width: 10px; height: 10px; background: #00ff66; border-radius: 50%; box-shadow: 0 0 8px #00ff66;"></span>
				</div>
				<div id="live-terminal-log" style="
					color: #4af626;
					font-family: 'Fira Code', 'Courier New', Courier, monospace;
					font-size: 13.5px;
					padding: 18px;
					height: 480px;
					overflow-y: auto;
					white-space: pre-wrap;
					line-height: 1.5;
				">$ Executing fetch_node_versions.sh...\n\n</div>
			</div>
		`);

		const $log = $wrapper.find("#live-terminal-log");

		frappe.realtime.on(event_name, (data) => {
			if (data && data.line) {
				$log.append(frappe.utils.escape_html(data.line));
				$log.scrollTop($log[0].scrollHeight);
			}
		});

		frm.call({
			doc: frm.doc,
			method: "fetch_node_version",
			callback(r) {
				frappe.realtime.off(event_name);
				$log.append("\n[SUCCESS] Shell execution completed successfully.\n");
				$log.scrollTop($log[0].scrollHeight);
				if (r.message && r.message.length) {
					frappe.msgprint({
						title: __("Node Versions Synced"),
						indicator: "green",
						message: __("Synced {0} Node version(s):<br><b>{1}</b>", [
							r.message.length,
							r.message.join(", ")
						])
					});
				}
			}
		});
	},

	fetch_python_version(frm) {
		const event_name = "python_version_shell_log";

		const d = new frappe.ui.Dialog({
			title: __("Live Shell Output - Fetch Python Versions"),
			size: "large",
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "terminal_html"
				}
			],
			primary_action_label: __("Close"),
			primary_action() {
				frappe.realtime.off(event_name);
				d.hide();
			}
		});

		d.show();

		d.$wrapper.find(".modal-dialog").css({
			"max-width": "920px",
			"width": "90%"
		});

		const $wrapper = d.get_field("terminal_html").$wrapper;
		$wrapper.html(`
			<div style="background: #121212; border-radius: 8px; border: 1px solid #2a2a2a; overflow: hidden;">
				<div style="background: #1e1e1e; padding: 8px 15px; border-bottom: 1px solid #2a2a2a; display: flex; align-items: center; justify-content: space-between;">
					<span style="color: #aaa; font-size: 12px; font-family: monospace;">bash &bull; fetch_python_versions.sh</span>
					<span style="display: inline-block; width: 10px; height: 10px; background: #00ff66; border-radius: 50%; box-shadow: 0 0 8px #00ff66;"></span>
				</div>
				<div id="live-python-terminal-log" style="
					color: #4af626;
					font-family: 'Fira Code', 'Courier New', Courier, monospace;
					font-size: 13.5px;
					padding: 18px;
					height: 480px;
					overflow-y: auto;
					white-space: pre-wrap;
					line-height: 1.5;
				">$ Executing fetch_python_versions.sh...\n\n</div>
			</div>
		`);

		const $log = $wrapper.find("#live-python-terminal-log");

		frappe.realtime.on(event_name, (data) => {
			if (data && data.line) {
				$log.append(frappe.utils.escape_html(data.line));
				$log.scrollTop($log[0].scrollHeight);
			}
		});

		frm.call({
			doc: frm.doc,
			method: "fetch_python_version",
			callback(r) {
				frappe.realtime.off(event_name);
				$log.append("\n[SUCCESS] Shell execution completed successfully.\n");
				$log.scrollTop($log[0].scrollHeight);
				if (r.message && r.message.length) {
					frappe.msgprint({
						title: __("Python Versions Synced"),
						indicator: "green",
						message: __("Synced {0} Python version(s):<br><b>{1}</b>", [
							r.message.length,
							r.message.join(", ")
						])
					});
				}
			}
		});
	},

	fetch_bench_list(frm) {
		const event_name = "bench_shell_log";

		const d = new frappe.ui.Dialog({
			title: __("Live Shell Output - Fetch Bench List"),
			size: "large",
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "terminal_html"
				}
			],
			primary_action_label: __("Close"),
			primary_action() {
				frappe.realtime.off(event_name);
				d.hide();
			}
		});

		d.show();

		d.$wrapper.find(".modal-dialog").css({
			"max-width": "920px",
			"width": "90%"
		});

		const $wrapper = d.get_field("terminal_html").$wrapper;
		$wrapper.html(`
			<div style="background: #121212; border-radius: 8px; border: 1px solid #2a2a2a; overflow: hidden;">
				<div style="background: #1e1e1e; padding: 8px 15px; border-bottom: 1px solid #2a2a2a; display: flex; align-items: center; justify-content: space-between;">
					<span style="color: #aaa; font-size: 12px; font-family: monospace;">bash &bull; fetch_bench_list.sh</span>
					<span style="display: inline-block; width: 10px; height: 10px; background: #00ff66; border-radius: 50%; box-shadow: 0 0 8px #00ff66;"></span>
				</div>
				<div id="live-bench-terminal-log" style="
					color: #4af626;
					font-family: 'Fira Code', 'Courier New', Courier, monospace;
					font-size: 13.5px;
					padding: 18px;
					height: 480px;
					overflow-y: auto;
					white-space: pre-wrap;
					line-height: 1.5;
				">$ Executing fetch_bench_list.sh...\n\n</div>
			</div>
		`);

		const $log = $wrapper.find("#live-bench-terminal-log");

		frappe.realtime.on(event_name, (data) => {
			if (data && data.line) {
				$log.append(frappe.utils.escape_html(data.line));
				$log.scrollTop($log[0].scrollHeight);
			}
		});

		frm.call({
			doc: frm.doc,
			method: "fetch_bench_list",
			callback(r) {
				frappe.realtime.off(event_name);
				$log.append("\n[SUCCESS] Bench discovery shell execution completed.\n");
				$log.scrollTop($log[0].scrollHeight);
				if (r.message && r.message.length) {
					frappe.msgprint({
						title: __("Benches Synced"),
						indicator: "green",
						message: __("Synced {0} Bench(es):<br><b>{1}</b>", [
							r.message.length,
							r.message.join(", ")
						])
					});
				}
			}
		});
	}
});
