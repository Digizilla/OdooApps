# -*- coding: utf-8 -*-
{
    'name': "mealshift_delivery_provider",

    'summary': """
        Integration with a delivery provider called 'mealshift' where the integration includes website and pos""",

    'description': """
        This addon is used for the integration between Odoo modules (Website, POS) and (Mealshift) provider.
        After setting the proper configurations for your provider account you can request for shipping price,
        publish order or cancel order via the API and Odoo website and POS orders creation and confirmation
    """,

    'author': "Digizilla",
    'website': "https://www.digizilla.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base', 'website_sale_delivery', 'base_geolocalize'], # Odoo 16 depends
    'depends': ['base', 'website', 'website_sale', 'stock_delivery', 'base_geolocalize', 'point_of_sale'], # maybe it can be required only for stock_delivery
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/shipping_methods_menu.xml',
        'views/website_add_address_template.xml',
        'views/delivery_mealshift.xml',
        'views/pos_order.xml',
        'views/sale_order.xml',
        'data/mealshift_delivery_carrier.xml',
    ],
    'assets': {
        'point_of_sale.assets_prod': [
            'mealshift_delivery_provider/static/src/js/pos_store.js',
            'mealshift_delivery_provider/static/src/js/order.js',
            'mealshift_delivery_provider/static/src/js/order_line.js',
            'mealshift_delivery_provider/static/src/js/payment_screen.js',
        ],
        'web.assets_qweb': [
            'mealshift_delivery_provider/static/src/xml/payment_screen.xml',
        ],
        'point_of_sale._assets_pos': [
            'mealshift_delivery_provider/static/src/xml/payment_screen.xml'
        ]
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True
}