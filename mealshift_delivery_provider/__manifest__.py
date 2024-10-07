# -*- coding: utf-8 -*-
{
    'name': "mealshift_delivery_provider",

    'summary': """
        Integration between Odoo modules (website, pos) and (Mealshift) delivery provider""",

    'description': """
        -- Addon purpose:
        This addon is used for the integration between Odoo modules (Website, POS) and (Mealshift) delivery provider.
        After setting the proper configurations for your provider account you can request for shipping price,
        publish order or cancel order via the API and Odoo website and POS orders creation and confirmation.
        
        -- Features:
        1- request shipping price from mealshift based on address 
        2- request shipping price from mealshift based on (latitude and longitude) values
        3- publish orders to mealshift
        4- cancel orders in mealshift
        5- create multiple shipping methods belongs to mealshift provider
        6- shipping methods can be now used in POS (mealshift) ones and other ones
        
        -- Benefits:
        1- POS has the ability of using shipping methods 
        2- integrate your shippings with Mealshift
        
        -- How to use:
        1- install mealshift_delivery_provider addon from the Apps
        2- From (POS configuration menu or Website configuration menu) access shipping methods
        3- Select mealshift shipping method and set your proper configurations (partner, id, secret)
        4- Set (available on pos) field to True if you want to use this shipping method in the POS module
        5- to use the mealshift inside the POS you will need to go the product that mealshift_delivery_provider creates
        which is called (Mealshift Delivery Product) go to (sale) tab and then select a category for that product so it can be 
        used in the pos.
        6- Go to POS or Website and make you can now select mealshift shipping method 
        7- retrieve the pricing from the shipping method based on your address or your latitude and longitude address values
        8- POS publish order: in pos the order is published to mealshift once the order is validated
        9- POS cancel order: in pos the order is canceled if you click on the "Cancel Delivery" button the pos.order form view
        10- Website publish order: in website the order is published into mealshift once you click on the "confirm" button the sale.order form view
        11- Website cancel order: in website the order is canceled once you click on the "cancel" button in the sale.order form view
        
        -- Technical details:
        - each webiste/pos have its unique mealshift identifier to be used in the “Partner ID” field of the mealshift integration settings
        the website/pos identifier is calculated as:
            if website: w + website_id
            if pos: p + pos_config_id
        - please when using inside POS module don't forget to select a category for the delivery product
        - publish the delivery method from it's form view to be available in the website
        - you can change the default base url if you are using test or prdouction enviroment 
        - please don't forget to set your (partner, id, secret) values
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
    "images": [
        "static/description/screenshot1.png",
        "static/description/screenshot2.png",
        "static/description/screenshot3.png",
        "static/description/screenshot4.png",
        "static/description/screenshot5.png",
        "static/description/screenshot6.png",
        "static/description/screenshot7.png",
        "static/description/screenshot8.png",
        "static/description/screenshot9.png",
    ],
    'installable': True,
    'application': True
}
