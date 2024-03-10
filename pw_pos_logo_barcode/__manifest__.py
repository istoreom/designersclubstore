# -*- coding: utf-8 -*-
{
    'name': 'Logo & Barcode on POS Receipt | Change POS Logo',
    'version': '1.0',
    'author': 'Preway IT Solutions',
    "sequence": 2,
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'summary': 'This module is allow to set Logo & Barcode on POS Receipt, Company Logo on POS Receipt and Screen, Pos Barcode Receipt | Change POS logo | Logo and Barcode | Pos Barcode Receipt | POS Logo Receipt',
    'description': """
  This module is allow to set Logo and Barocode on pos receipt
- POS Logo on Receipt
- POS Barcode on Receipt
- POS Logo on Screen
- Company Logo on POS Screen 
    """,
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pw_pos_logo_barcode/static/src/js/JsBarcode.all.min.js',
            'pw_pos_logo_barcode/static/src/js/Chrome.js',
            'pw_pos_logo_barcode/static/src/js/pos_store.js',
            'pw_pos_logo_barcode/static/src/xml/**/*',
        ],
    },
    'currency': "EUR",
    'application': True,
    'installable': True,
    "auto_install": False,
    "license": "LGPL-3",
    "images":["static/description/Banner.png"],
}
