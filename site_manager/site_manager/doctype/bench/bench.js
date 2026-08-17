frappe.ui.form.on("Bench", {
	setup(frm) {
		frappe.realtime.on("bench_shell_log", (data) => {
			if (data && data.line) {
				if ($("#live-bench-log").length) {
					$("#live-bench-log").append(frappe.utils.escape_html(data.line));
					$("#live-bench-log").scrollTop($("#live-bench-log")[0].scrollHeight);
				}
			}
		});
	},
	before_save(frm) {
		if (frm.is_new()) {
			const d = new frappe.ui.Dialog({
				title: __("Live Shell Log - Bench Initialization"),
				size: "large",
				fields: [{ fieldtype: "HTML", fieldname: "log_html" }],
				primary_action_label: __("Close"),
				primary_action() {
					frappe.realtime.off("bench_shell_log");
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
			frm._live_dialog = d;
		}
	},
	after_save(frm) {
		if (frm._live_dialog) {
			$("#live-bench-log").append("\n[SUCCESS] Bench initialization complete.\n");
			$("#live-bench-log").scrollTop($("#live-bench-log")[0].scrollHeight);
			setTimeout(() => {
				if (frm._live_dialog) {
					frm._live_dialog.hide();
					frm._live_dialog = null;
				}
			}, 1200);
		}
	}
});
