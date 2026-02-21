frappe.ui.form.on('Control de Merma', {
    refresh: function (frm) {
    }
});

frappe.ui.form.on('Detalle de Merma', {
    cantidad: function (frm, cdt, cdn) {
        calculate_total(frm, cdt, cdn);
    },
    costo_unitario: function (frm, cdt, cdn) {
        calculate_total(frm, cdt, cdn);
    }
});

function calculate_total(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    frappe.model.set_value(cdt, cdn, 'costo_total', (row.cantidad || 0) * (row.costo_unitario || 0));

    let total = 0;
    frm.doc.detalle.forEach(d => {
        total += d.costo_total || 0;
    });
    frm.set_value('costo_total', total);
}
