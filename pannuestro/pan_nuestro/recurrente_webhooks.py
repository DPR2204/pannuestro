import frappe
import json

@frappe.whitelist(allow_guest=True)
def handle_webhook():
    """
    Maneja las notificaciones de pago (webhooks) de Recurrente.
    """
    if frappe.request.method != "POST":
        frappe.throw("Método no permitido", frappe.PermissionError)

    data = json.loads(frappe.request.data)
    frappe.log_error(f"Recurrente Webhook Received: {json.dumps(data, indent=2)}", "Recurrente Webhook")

    # TODO: Verificar firma del webhook con webhook_secret de Recurrente Settings

    # Ejemplo de estructura de Recurrente (ajustar según docs reales)
    # Suponiendo que el evento es 'checkout.completed' y tiene metadatos o el ID en la descripción
    event = data.get("event") or data.get("type")
    
    # En Recurrente, usualmente recibimos información del checkout
    checkout = data.get("checkout") or data.get("data", {}).get("object")
    
    if not checkout:
        return {"status": "ignored"}

    # Intentar obtener el nombre de la factura. 
    # Podríamos haberlo pasado en 'external_id' o similar si la API lo permite.
    # Por ahora buscamos en los items o descripción si el client lo puso.
    # Una forma segura es guardar el checkout_id en la factura al crear el link.
    
    # Supongamos que pasamos el nombre de la factura en el success_url 
    # o que Recurrente nos lo devuelve de alguna forma.
    # Buscamos facturas pendientes que coincidan con el monto si no hay ID claro.
    
    # OPTIMIZACIÓN: Al crear el checkout, deberíamos guardar el ID de Recurrente en la Sales Invoice.
    # Por ahora, buscaremos por el campo 'custom_recurrente_id' (que crearemos).
    
    # NOTA: Para que esto sea robusto, necesitamos añadir campos personalizados a Sales Invoice.
    
    return {"status": "ok"}

def create_payment_entry(invoice_name, amount, reference_id):
    """
    Crea un Payment Entry para una factura pagada por Recurrente.
    """
    invoice = frappe.get_doc("Sales Invoice", invoice_name)
    
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer"
    pe.party = invoice.customer
    pe.paid_amount = amount
    pe.received_amount = amount
    pe.reference_no = reference_id
    pe.reference_date = frappe.utils.nowdate()
    
    pe.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": invoice_name,
        "total_amount": invoice.grand_total,
        "outstanding_amount": invoice.outstanding_amount,
        "allocated_amount": amount
    })
    
    pe.insert()
    pe.submit()
    return pe
