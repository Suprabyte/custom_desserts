# custom_desserts/__manifest__.py
{
    'name': 'Gestión de Postres v2',
    'version': '18.0.1.0.0',
    'summary': 'Módulo para la gestión de producción de postres.',
    'author': 'Sr. Christian Carreno',
    'website': 'https://www.rubro.pe',
    'license': 'LGPL-3',
    'category': 'Manufacturing',
    'depends': ['base', 'mrp', 'product', 'uom', 'stock', 'calendar'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/bom_line_views.xml',      # Se cargan primero las vistas de las líneas
        'views/dessert_views.xml',       # Luego las vistas principales
        'views/calendar_views.xml',
    ],
    'installable': True,
    'application': True,
}