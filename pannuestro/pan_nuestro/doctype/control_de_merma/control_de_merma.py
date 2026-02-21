import frappe
from frappe.model.document import Document

class ControdeMerma(Document):
    def validate(self):
        self.calculate_costs()

    def calculate_costs(self):
        total_cost = 0
        for item in self.detalle:
            item.costo_total = (item.cantidad or 0) * (item.costo_unitario or 0)
            total_cost += item.costo_total
        self.costo_total = total_cost

    def on_submit(self):
        self.create_stock_entry()

    def create_stock_entry(self):
        """
        Crea un Stock Entry de tipo 'Material Issue' para descontar la merma del inventario.
        """
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Issue"
        se.company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")
        se.posting_date = self.fecha
        se.remarks = f"Merma registrada en {self.name}: {self.tipo_merma}"
        
        # Bodega predeterminada (Asunción: 'Stores' o similar)
        default_warehouse = frappe.db.get_value("Warehouse", {"is_group": 0, "company": se.company}, "name")

        for item in self.detalle:
            se.append("items", {
                "item_code": item.producto,
                "qty": item.cantidad,
                "uom": item.uom,
                "s_warehouse": default_warehouse,
                "expense_account": "Stock Adjustment - PN" # Cuenta de gasto para merma (debe existir)
            })
        
        se.insert()
        se.submit()
        frappe.msgprint(f"Se ha creado el movimiento de stock {se.name} para descontar la merma.")
