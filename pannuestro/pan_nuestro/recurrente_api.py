import frappe
import requests
import json

class RecurrenteAPI:
    def __init__(self):
        self.settings = frappe.get_doc("Recurrente Settings")
        if not self.settings.enabled:
            frappe.throw("La integración con Recurrente no está habilitada en Recurrente Settings")
        
        self.api_key = self.settings.get_password("api_key")
        self.secret_key = self.settings.get_password("secret_key")
        
        if self.settings.environment == "Sandbox":
            self.base_url = self.settings.sandbox_url or "https://app.recurrente.com/api"
        else:
            self.base_url = self.settings.production_url
            
        if not self.base_url:
            frappe.throw("URL de API no configurada para el entorno seleccionado")

        self.headers = {
            "Content-Type": "application/json",
            "X-PUBLIC-KEY": self.api_key,
            "X-SECRET-KEY": self.secret_key
        }

    def create_checkout(self, invoice_doc):
        """
        Crea un checkout en Recurrente para una Sales Invoice de Frappe.
        """
        endpoint = f"{self.base_url}/checkouts"
        
        # Preparar los items para Recurrente
        items = []
        for item in invoice_doc.items:
            items.append({
                "name": item.item_name or item.item_code,
                "amount": float(item.amount),
                "quantity": int(item.qty)
            })
            
        payload = {
            "checkout": {
                "success_url": frappe.utils.get_url(f"/api/method/pannuestro.recurrente.recurrente_api.payment_success?invoice={invoice_doc.name}"),
                "cancel_url": frappe.utils.get_url(f"/app/sales-invoice/{invoice_doc.name}"),
                "currency": invoice_doc.currency,
                "items_attributes": items
            }
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            return data.get("checkout_url")
        except requests.exceptions.HTTPError as e:
            frappe.log_error(f"Recurrente API Error: {response.text}", "Recurrente API")
            frappe.throw(f"Error al crear el checkout en Recurrente: {response.text}")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Recurrente API")
            frappe.throw(f"Error inesperado al conectar con Recurrente: {str(e)}")

@frappe.whitelist()
def create_payment_link(invoice_name):
    """
    Función llamada desde el frontend para generar el link de pago.
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    
    # Validaciones básicas
    if doc.docstatus != 1:
        frappe.throw("La factura debe estar validada (Submitted) para cobrar")
    if doc.outstanding_amount <= 0:
        frappe.throw("La factura ya está pagada")
        
    api = RecurrenteAPI()
    checkout_url = api.create_checkout(doc)
    
    # Guardar el link en la factura (podríamos añadir un campo custom después)
    # Por ahora solo lo retornamos
    return checkout_url

@frappe.whitelist(allow_guest=True)
def payment_success(invoice):
    """
    Redirección simple de éxito.
    El webhook procesará el pago real.
    """
    frappe.local.response.type = "redirect"
    frappe.local.response.location = frappe.utils.get_url(f"/app/sales-invoice/{invoice}")
