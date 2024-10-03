# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSaleForm
import logging
_logger = logging.getLogger(__name__)

class GeoLocalizeWebsiteSaleForm(WebsiteSaleForm):

    # overrided function
    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values = {}
        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        print("This is authorized fields from overrided function", authorized_fields)
        authorized_fields.update({'partner_longitude': {}, 'partner_latitude': {}})
        for k, v in values.items():
            # don't drop empty value, it could be a field to reset
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:  # DEBUG ONLY
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'): # classic case
                    _logger.debug("website_sale postprocess: %s value has been dropped (empty or not writable)" % k)

        if request.website.specific_user_account:
            new_values['website_id'] = request.website.id

        if mode[0] == 'new':
            new_values['company_id'] = request.website.company_id.id
            new_values['team_id'] = request.website.salesteam_id and request.website.salesteam_id.id
            new_values['user_id'] = request.website.salesperson_id.id

        lang = request.lang.code if request.lang.code in request.website.mapped('language_ids.code') else None
        if lang:
            new_values['lang'] = lang
        if mode == ('edit', 'billing') and order.partner_id.type == 'contact':
            new_values['type'] = 'other'
        if mode[1] == 'shipping':
            new_values['parent_id'] = order.partner_id.commercial_partner_id.id
            new_values['type'] = 'delivery'

        return new_values, errors, error_msg
    # @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    # def address(self, **kw):



# class MealshiftDeliveryProvider(http.Controller):
#     @http.route('/mealshift_delivery_provider/mealshift_delivery_provider', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mealshift_delivery_provider/mealshift_delivery_provider/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mealshift_delivery_provider.listing', {
#             'root': '/mealshift_delivery_provider/mealshift_delivery_provider',
#             'objects': http.request.env['mealshift_delivery_provider.mealshift_delivery_provider'].search([]),
#         })

#     @http.route('/mealshift_delivery_provider/mealshift_delivery_provider/objects/<model("mealshift_delivery_provider.mealshift_delivery_provider"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mealshift_delivery_provider.object', {
#             'object': obj
#         })
