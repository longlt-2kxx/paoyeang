{
    'name': 'User Warehouse Access Control',
    'version': '14.0.1.0.0',
    'summary': 'Add allowed warehouse and location fields to user form',
    'description': """
        This module allows admin to configure which warehouses and locations
        a user is allowed to access. The settings appear in the User Preferences tab.
    """,
    'author': 'Jackie Ly',
    'category': 'Inventory',
    'depends': ['sale','base', 'stock',  'sale_stock'],

    'data': [
        'security/ir_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'views/assets.xml',
        'views/clone_access.xml',
        'views/res_users_views.xml',
        'views/sale_order_views.xml',
        'views/stock_location_views.xml',
        'views/product_replenish_views.xml',
        'views/forecast_line_views.xml',
        'views/forecast_wizard_views.xml',
        'views/sale_reporting.xml',
        'views/clone_access.xml',
        'views/stock_warehouse_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
