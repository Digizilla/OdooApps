# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from ..models.mealshift_api_methods import request_quote
import logging
_logger = logging.getLogger(__name__)


class AttributeDict:
    def __init__(self, d):
        self.pos_order = True
        self.__dict__.update(d)

class PosMealShiftDeliveryProvider(http.Controller):
    @http.route('/pos/mealshift-delivery-provider/request-quote', type='json', auth='public')
    def request_quote(self, delivery_method_id, order):
        order = AttributeDict(order)
        mealshift_delivery_method = request.env['delivery.carrier'].search([('id', '=', delivery_method_id)])
        partner_shipping_id = request.env['res.partner'].search([('id', '=', order.partner_shipping_id['id'])])
        pos_config_id = request.env['pos.config'].search([('id', '=', order.website_id['id'])])
        order.partner_shipping_id = partner_shipping_id
        order.website_id = pos_config_id
        if (order.pricelist_id):
            pricelist_id = request.env['product.pricelist'].search([('id', '=', order.pricelist_id['id'])])
            order.pricelist_id = pricelist_id


        rate_shipment_method = getattr(mealshift_delivery_method, f"{mealshift_delivery_method.delivery_type}_rate_shipment", None)
        result = {
            'price': None,
            'error_message': "POS should have a pricelist"
        }
        if (mealshift_delivery_method.delivery_type == 'fixed' and not order.pricelist_id):
            return result;

        if (rate_shipment_method):
            result = rate_shipment_method(order)


        return result
