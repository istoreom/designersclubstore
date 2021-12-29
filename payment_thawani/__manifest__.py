# -*- coding: utf-8 -*-
{
    'name': u'Thawani Payment Acquirer',
    'version': '14.0.1.0.0',
    'category': 'Thawani Payment Integration',
    'summary': "Thawani Payment gateway, provided by Omani company Thawani Technologies, is a smart, simple, and secure e-payment services that cater for user's and merchant's needs alike. Thawani is the leading fintech solution in the middle east countries.",
    'website': 'https://silentinfotech.com',
    'live_test_url': 'https://silentinfotech.com/blog/thawani-payment-system-integration-with-odoo',
    'description': u"""
    This module through payment applicable to all the users using Thawani fintech. The Payment to be made via thawani payment gateway will be always with Omani Rial so user don't need to worry about currency at the same time it will store order amount in different currencies in Odoo based on currency rate configured. 
""",
    'author': u'Silent Infotech Pvt. Ltd.',
    'price': 850.000,
    'currency': 'USD',
    'depends': [
        'account', 'payment', 'sale', 'website', 'website_sale'
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'test': [],

    'data': [
            'views/thawani_view_template.xml',
            'data/pages.xml',
            'data/thawani_acquirer.xml',
            'views/payment_acquirer.xml',
    ],
    'images': ['static/description/banner.png'],
    'qweb': [

    ],

    'application': True,
    'installable': True,
    'auto_install': False,
    'license': u'OPL-1',
}
