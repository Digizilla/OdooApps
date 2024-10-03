# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields, _
import requests
from odoo.exceptions import UserError
from odoo.tools import pdf

from .mealshift_api_methods import request_quote

# from .ups_request import upsRequest

#


class ProviderMealShift(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('mealshift', "MealShift")
    ], ondelete={'mealshift': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    mealshift_base_url = fields.Char()
    mealshift_partner = fields.Char()
    mealshift_ms_partner_id = fields.Char()
    mealshift_secret = fields.Char()

    published_on_pos = fields.Boolean(default=False)
    product_barcode = fields.Char(compute="_compute_product_barcode")

    @api.depends('product_id')
    def _compute_product_barcode(self):
        for record in self:
            if record.product_id:
                record.product_barcode = record.product_id.barcode
            else:
                record.product_barcode = ""

    def mealshift_rate_shipment(self, order):
        configuration_parameters = {
            "id": str(self.id),
            "base_url": self.mealshift_base_url,
            "partner": self.mealshift_partner,
            "ms_partner_id": self.mealshift_ms_partner_id,
            "secret": self.mealshift_secret
        }

        for configuration_parameter in configuration_parameters:
            if not configuration_parameters[configuration_parameter] or configuration_parameters[configuration_parameter] == "":
                return {'success': False,
                        'price': None,
                        'error_message': 'Delivery method configuration error!',
                        'warning_message': False}

        address_params = [
            order.partner_shipping_id.zip,
            order.partner_shipping_id.country_id.name,
            order.partner_shipping_id.state_id.name if order.partner_shipping_id.state_id else "",
            order.partner_shipping_id.city,
            order.partner_shipping_id.street if order.partner_shipping_id.street else ""
        ]

        for address_param in address_params:
            if not address_param:
                return {'success': False,
                        'price': None,
                        'error_message': 'Full partner address is required!',
                        'warning_message': False}

        address_str = " ".join(address_params)
        latitude = order.partner_shipping_id.partner_latitude
        longitude = order.partner_shipping_id.partner_longitude

        clientReference = "p" + str(order.website_id.id) if getattr(order, 'pos_order', None) else 'w' + str(order.website_id.id)
        data = {
            "clientReference": clientReference, # I've named pos.session as website_id also in the controller
            "address": address_str
        }

        if latitude:
            data.update({'latitude': latitude, 'longitude': longitude})

        amount, currency = request_quote(configuration_parameters, data)
        print("this is amount: ", amount, "this is currency: ", currency)

        if currency:
            return {'success': True,
                    'price': amount,
                    'error_message': False,
                    'warning_message': False}
        else:
            return {'success': False,
                    'price': None,
                    'error_message': 'Unknown error!',
                    'warning_message': False}
