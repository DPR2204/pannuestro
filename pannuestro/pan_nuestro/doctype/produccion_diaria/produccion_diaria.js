frappe.ui.form.on('Produccion Diaria', {
    refresh: function (frm) {
        if (frm.doc.estado === 'Planificado' && !frm.doc.__islocal) {
            frm.add_custom_button(__('Crear Órdenes de Producción'), function () {
                frm.call('create_work_orders').then(r => {
                    frm.refresh();
                });
            });

            frm.add_custom_button(__('Verificar Materia Prima'), function () {
                frm.call('get_raw_materials_needed').then(r => {
                    if (r.message) {
                        let html = '<table class="table table-bordered"><thead><tr><th>Material</th><th>Cantidad Necesaria</th></tr></thead><tbody>';
                        for (let item in r.message) {
                            html += `<tr><td>${item}</td><td>${r.message[item]}</td></tr>`;
                        }
                        html += '</tbody></table>';

                        frappe.msgprint({
                            title: __('Materia Prima Necesaria'),
                            message: html,
                            wide: true
                        });
                    }
                });
            });
        }
    }
});

frappe.ui.form.on('Detalle de Produccion', {
    cantidad_planificada: function (frm, cdt, cdn) {
        calculate_diff(frm, cdt, cdn);
    },
    cantidad_producida: function (frm, cdt, cdn) {
        calculate_diff(frm, cdt, cdn);
    }
});

function calculate_diff(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    frappe.model.set_value(cdt, cdn, 'diferencia', (row.cantidad_producida || 0) - (row.cantidad_planificada || 0));
}
