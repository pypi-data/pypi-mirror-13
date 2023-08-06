# -*- coding: UTF-8 -*-
'''
    product

    :copyright: (c) 2013-2015 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
'''
from trytond.transaction import Transaction
from trytond.pool import PoolMeta, Pool
from decimal import Decimal


__all__ = [
    'Product',
]
__metaclass__ = PoolMeta


class Product:
    "Product"

    __name__ = "product.product"

    @classmethod
    def extract_product_values_from_ebay_data(cls, product_data):
        """
        Extract product values from the ebay data, used for
        creation of product. This method can be overwritten by
        custom modules to store extra info to a product

        :param: product_data
        :returns: Dictionary of values
        """
        SaleChannel = Pool().get('sale.channel')

        ebay_channel = SaleChannel(Transaction().context['current_channel'])
        ebay_channel.validate_ebay_channel()
        return {
            'name': product_data['Item']['Title'],
            'default_uom': ebay_channel.default_uom.id,
            'salable': True,
            'sale_uom': ebay_channel.default_uom.id,
        }

    @classmethod
    def create_from(cls, channel, product_data):
        """
        Create product for channel
        """
        if channel.source != 'ebay':
            return super(Product, cls).create_from(channel, product_data)
        return cls.create_using_ebay_data(product_data)

    @classmethod
    def create_using_ebay_data(cls, product_data):
        """
        Create a new product with the `product_data` from ebay.

        :param product_data: Product Data from eBay
        :returns: Browse record of product created
        """
        Template = Pool().get('product.template')

        product_values = cls.extract_product_values_from_ebay_data(
            product_data
        )

        product_values.update({
            'products': [('create', [{
                'description': product_data['Item']['Description'],
                'list_price': Decimal(
                    product_data['Item']['BuyItNowPrice']['value'] or
                    product_data['Item']['StartPrice']['value']
                ),
                'cost_price':
                    Decimal(product_data['Item']['StartPrice']['value']),
                'code':
                    product_data['Item'].get('SKU', None) and
                    product_data['Item']['SKU'] or None,
            }])],
        })

        product_template, = Template.create([product_values])

        return product_template.products[0]
