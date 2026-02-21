frappe.ui.form.on('Pedido Especial', {
    refresh: function (frm) {
    },
    total: function (frm) {
        calculate_balance(frm);
    },
    anticipo: function (frm) {
        calculate_balance(frm);
    }
});

function calculate_balance(frm) {
    frm.set_value('saldo', (frm.doc.total || 0) - (frm.doc.anticipo || 0));
}
