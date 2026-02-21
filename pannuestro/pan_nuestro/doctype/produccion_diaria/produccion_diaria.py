import frappe
from frappe.model.document import Document

class ProduccionDiaria(Document):
    def validate(self):
        self.calculate_differences()

    def calculate_differences(self):
        for item in self.detalle:
            item.diferencia = (item.cantidad_producida or 0) - (item.cantidad_planificada or 0)

    @frappe.whitelist()
    def create_work_orders(self):
        """
        Crea Órdenes de Producción (Work Orders) para cada item en el detalle.
        """
        if self.estado != "Planificado":
            frappe.throw("Solo se pueden crear órdenes de producción si el estado es 'Planificado'")

        created_orders = []
        for item in self.detalle:
            if item.cantidad_planificada <= 0:
                continue
                
            # Buscar el BOM predeterminado del item
            bom = frappe.db.get_value("BOM", {"item": item.producto, "is_default": 1, "docstatus": 1})
            if not bom:
                frappe.msgprint(f"Advertencia: El producto {item.producto} no tiene un BOM (Lista de Materiales) predeterminado y validado. No se creó orden de producción.")
                continue

            wo = frappe.new_doc("Work Order")
            wo.production_item = item.producto
            wo.bom_no = bom
            wo.qty = item.cantidad_planificada
            wo.planned_start_date = self.fecha
            wo.company = frappe.defaults.get_user_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")
            wo.wip_warehouse = frappe.db.get_value("Warehouse", {"is_group": 0, "company": wo.company}, "name") # Asunción de bodega WIP
            
            wo.insert()
            created_orders.append(wo.name)
        
        if created_orders:
            self.estado = "En Proceso"
            self.save()
            frappe.msgprint(f"Se crearon las siguientes Órdenes de Producción: {', '.join(created_orders)}")
        else:
            frappe.throw("No se pudo crear ninguna Orden de Producción. Verifique que los productos tengan BOMs válidos.")

    @frappe.whitelist()
    def get_raw_materials_needed(self):
        """
        Calcula el total de materia prima necesaria basada en los BOMs.
        """
        total_materials = {}
        for item in self.detalle:
            if item.cantidad_planificada <= 0:
                continue
                
            bom = frappe.db.get_value("BOM", {"item": item.producto, "is_default": 1, "docstatus": 1})
            if not bom:
                continue
            
            bom_doc = frappe.get_doc("BOM", bom)
            for exploded_item in bom_doc.exploded_items:
                raw_item = exploded_item.item_code
                qty_needed = exploded_item.qty_consumed_per_unit * item.cantidad_planificada
                
                if raw_item in total_materials:
                    total_materials[raw_item] += qty_needed
                else:
                    total_materials[raw_item] = qty_needed
        
        return total_materials
