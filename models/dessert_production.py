# custom_desserts/models/dessert_production.py
from odoo import models, fields, api
from odoo.exceptions import UserError

class Dessert(models.Model):
    _name = 'dessert.dessert'
    _description = 'Postre'

    name = fields.Char('Nombre del Postre', required=True)
    dessert_type = fields.Selection([
        ('finished', 'Producto Terminado'),
        ('intermediate', 'Producto Intermedio')
    ], string='Tipo de Postre', required=True)
    
    # Relación con los insumos (Lista de Materiales)
    bom_line_ids = fields.One2many('dessert.bom.line', 'dessert_id', string='Insumos')
    
    # Campo para enlazar con el producto de Odoo
    product_id = fields.Many2one('product.product', string='Producto Asociado',
                                 help="Producto en el inventario que representa este postre.")

class DessertBomLine(models.Model):
    _name = 'dessert.bom.line'
    _description = 'Línea de Insumos para Postre'

    dessert_id = fields.Many2one(
        'dessert.dessert',
        string='Postre',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Insumo',
        required=True,
        domain="[('purchase_ok','=',True),('detailed_type','=','product')]"
    )
    quantity = fields.Float('Cantidad', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', related='product_id.uom_id', readonly=True)

class ProductionOrder(models.Model):
    _name = 'dessert.production.order'
    _description = 'Orden de Producción de Postre'

    name = fields.Char('Referencia', required=True, copy=False, readonly=True, 
                       default=lambda self: self.env['ir.sequence'].next_by_code('dessert.production.order'))
    dessert_id = fields.Many2one('dessert.dessert', string='Postre a Producir', required=True)
    quantity_to_produce = fields.Float('Cantidad a Producir', required=True, default=1.0)
    production_date = fields.Datetime('Fecha de Producción', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('in_progress', 'En Proceso'),
        ('done', 'Hecho'),
        ('cancel', 'Cancelado')
    ], string='Estado', default='draft')
    
    # Campos para lote y fecha de vencimiento
    lot_id = fields.Many2one('stock.production.lot', string='Lote de Producción', readonly=True)
    expiration_date = fields.Date('Fecha de Vencimiento')

    def action_confirm(self):
        self.state = 'confirmed'

    def action_start_production(self):
        # Aquí se crea el movimiento de stock
        for order in self:
            if not order.dessert_id.bom_line_ids:
                raise UserError('No se han definido insumos para este postre.')

            # Crear el movimiento de stock para los insumos
            move_lines = []
            location_stock = self.env.ref('stock.stock_location_stock')
            location_production = self.env.ref('stock.stock_location_production')

            for line in order.dessert_id.bom_line_ids:
                move_lines.append((0, 0, {
                    'name': f'Insumo: {line.product_id.name}',
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity * order.quantity_to_produce,
                    'product_uom': line.uom_id.id,
                    'location_id': location_stock.id,
                    'location_dest_id': location_production.id
                }))
            
            # Crear la transferencia
            stock_picking = self.env['stock.picking'].create({
                'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                'location_id': location_stock.id,
                'location_dest_id': location_production.id,
                'move_lines': move_lines
            })
            
            stock_picking.action_confirm()
            stock_picking.action_assign()
            
            order.state = 'in_progress'
        return True


    def action_mark_done(self):
        for order in self:
            if not order.dessert_id.product_id:
                raise UserError("El postre no tiene un 'Producto Asociado' configurado.")
            
            # Crear lote y fecha de vencimiento para el producto terminado
            lot = self.env['stock.production.lot'].create({
                'name': self.env['ir.sequence'].next_by_code('stock.lot.serial') or order.name,
                'product_id': order.dessert_id.product_id.id,
                'company_id': self.env.company.id,
                'expiration_date': order.expiration_date,
            })
            order.lot_id = lot
            order.state = 'done'
        return True
