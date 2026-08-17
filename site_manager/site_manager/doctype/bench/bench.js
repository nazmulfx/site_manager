frappe.ui.form.on("Bench", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Execute Initialization"), function() {
				const event_name = "bench_shell_log";

				const d = new frappe.ui.Dialog({
					title: __("Live Shell Output - Bench Initialization"),
					size: "large",
					fields: [{ fieldtype: "HTML", fieldname: "log_html" }],
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

				const $wrapper = d.get_field("log_html").$wrapper;
				$wrapper.html(`
					<div style="background: #121212; border-radius: 8px; border: 1px solid #2a2a2a; overflow: hidden;">
						<div style="background: #1e1e1e; padding: 8px 15px; border-bottom: 1px solid #2a2a2a; display: flex; align-items: center; justify-content: space-between;">
							<span style="color: #aaa; font-size: 12px; font-family: monospace;">bash &bull; create_bench.sh</span>
							<span style="display: inline-block; width: 10px; height: 10px; background: #00ff66; border-radius: 50%; box-shadow: 0 0 8px #00ff66;"></span>
						</div>
						<div id="live-bench-log" style="
							color: #4af626;
							font-family: 'Fira Code', 'Courier New', Courier, monospace;
							font-size: 13.5px;
							padding: 18px;
							height: 460px;
							overflow-y: auto;
							white-space: pre-wrap;
							line-height: 1.5;
						">$ Executing create_bench.sh...\n\n</div>
					</div>
				`);

				const $log = $wrapper.find("#live-bench-log");

				frappe.realtime.on(event_name, (data) => {
					if (data && data.line) {
						$log.append(frappe.utils.escape_html(data.line));
						$log.scrollTop($log[0].scrollHeight);
					}
				});

				frm.call({
					doc: frm.doc,
					method: "execute_initialization",
					callback(r) {
						frappe.realtime.off(event_name);
						$log.append("\n[SUCCESS] Bench initialization complete.\n");
						$log.scrollTop($log[0].scrollHeight);
						frappe.msgprint({
							title: __("Initialization Complete"),
							indicator: "green",
							message: __("Successfully initialized bench.")
						});
						frm.reload_doc();
					}
				});
			}).addClass("btn-primary");
		}
	}
});
