frappe.ui.form.on("Room Booking", {
    refresh: function(frm) {
        // Only show QR code if submitted and exists
        if(frm.doc.docstatus === 1 && frm.doc.qr_code) {
            let qr_div = frm.get_field("qr_code_html").$wrapper;
            qr_div.empty(); // Clear any old QR
            qr_div.append(`
                <img src="${frm.doc.qr_code}" width="200" height="200" />
            `);

            // Show check-in status
            if(frm.doc.check_in_status) {
                qr_div.append(`<p><strong>Status:</strong> ${frm.doc.check_in_status}</p>`);
            }
        } else {
            // Clear QR if not submitted
            frm.get_field("qr_code_html").$wrapper.empty();
        }
    }
});
