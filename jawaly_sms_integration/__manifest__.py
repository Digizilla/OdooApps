# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '4Jawaly SMS Integration',
    'version': '1.2',
    'category': 'sms',
    'sequence': 100,
    'summary': 'Jawaly SMS Integration api',
    'description': "Integrate jawaly sms api with odoo sms_gateway module",
    'website': 'https://www.odoo.com/page/crm',
    'application': True,
    'author': "Digizilla",
    'website': "https://www.digizilla.net",
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sms',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/jawaly_sms_configs.xml',
        'views/jawaly_senders.xml',
        'views/jawaly_log.xml'

    ],
    'assets': {
        'web.assets_backend': [
            'jawaly_sms_integration/static/src/xml/templates.xml',
            'jawaly_sms_integration/static/src/js/sms_button.js',
        ]
    },
    "images": [
        "static/description/img1.png",
        "static/description/img2.png",
        "static/description/img3.png",
        "static/description/img4.png",
        "static/description/img5.png",
        "static/description/img6.png",
        "static/description/img7.png",
        "static/description/img8.png",
        "static/description/img9.png",
        "static/description/img10.png",
        "static/description/img11.png",
        "static/description/img12.png",
        "static/description/img13.png",
        "static/description/img14.png",
        "static/description/img15.png",
    ],
}