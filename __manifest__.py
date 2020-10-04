{
    'name': 'Pricelist Product Template',
    'author': 'technoindo.com',
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Summary the addon.',
    'description': '''Description the addon'''
                   ,
    'depends': ['point_of_sale', 'product', 'sale'],
    'data': [
        'views/pos_order.xml',
        'views/pricelist_product_template.xml',
        'views/pricelist_product_views.xml',
    ],
    'qweb': [
        'static/src/xml/pos_uoms_price.xml',
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
