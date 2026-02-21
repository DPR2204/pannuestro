frappe.ui.form.on('Sales Invoice', {
    refresh: function (frm) {
        // Solo mostrar si la factura está validada (Submitted) y tiene saldo pendiente
        if (frm.doc.docstatus === 1 && frm.doc.outstanding_amount > 0) {
            frm.add_custom_button(__('Cobrar con Recurrente'), function () {
                frappe.call({
                    method: 'pannuestro.pan_nuestro.recurrente_api.create_payment_link',
                    args: {
                        invoice_name: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            // Abrir el link de pago en una pestaña nueva
                            window.open(r.message, '_blank');

                            frappe.msgprint({
                                title: __('Link de Pago Generado'),
                                indicator: 'green',
                                message: __('Se ha abierto el link de pago en una nueva pestaña. También puedes copiarlo desde aquí: <br><br><b>' + r.message + '</b>')
                            });
                        }
                    }
                });
            }, __('Acciones'));
        }
    }
});
