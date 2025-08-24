# models/calendar_event.py
from odoo import models, fields

class CalendarEvent(models.Model):
    # 1. Indicamos que vamos a heredar (extender) un modelo existente
    _inherit = 'calendar.event' 

    # 2. Añadimos nuestro nuevo campo
    production_order_id = fields.Many2one(
        'dessert.production.order',      # El modelo al que queremos enlazar
        string='Orden de Producción de Postre' # La etiqueta que verá el usuario
    )