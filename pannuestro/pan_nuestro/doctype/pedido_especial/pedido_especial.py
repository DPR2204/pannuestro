import frappe
from frappe.model.document import Document

class PedidoEspecial(Document):
    def validate(self):
        self.calculate_balance()

    def calculate_balance(self):
        self.saldo = (self.total or 0) - (self.anticipo or 0)

    def on_update(self):
        if self.estado == "Entregado" and not self.invoice_created:
            self.create_sales_invoice()

    def create_sales_invoice(self):
        """
        Crea automáticamente una Sales Invoice cuando el pedido se marca como Entregado.
        """
        invoice = frappe.new_doc("Sales Invoice")
        invoice.customer = self.cliente
        invoice.due_date = frappe.utils.nowdate()
        invoice.custom_pedido_especial = self.name # Referencia cruzada
        
        # Añadir ítem genérico para el pedido especial (o mapear si tenemos ítems)
        invoice.append("items", {
            "item_name": f"Pedido Especial: {self.name}",
            "description": self.descripcion,
            "qty": 1,
            "rate": self.total,
            "income_account": "Sales - PN" # Debe existir
        })
        
        # Aplicar el anticipo si existe
        if self.anticipo > 0:
            invoice.append("advances", {
                # Aquí iría la lógica para vincular el pago del anticipo
            })
            
        invoice.insert()
        # invoice.submit() # Opcional: dejar en borrador para revisión
        
        frappe.msgprint(f"Se ha generado la factura {invoice.name} para este pedido.")
        self.db_set("invoice_created", 1)
