from odoo import models, fields, api, _
from .mealshift_api_methods import publish_order, cancel_order

class MealshiftSaleOrder(models.Model):
    _inherit = 'sale.order'

    mealshift_status = fields.Selection([
        ('not_published', 'Not Published'),
        ('published', 'Published'),
        ('canceled', 'Canceled')
    ],string="Mealshift Status", readonly=True, required=False, default='not_published')
    mealshift_status_reason = fields.Char(string="Mealshift Status Reason", required=False, default="", readonly=True)
    mealshift_order_id = fields.Char(string="Mealshift Order ID", required=False, default="", readonly=True)
    mealshift_partner_reference = fields.Char(string="Mealshift Partner Reference", required=False, defualt="", readonly=True)

    @api.model
    def create(self, vals):
        record = super(MealshiftSaleOrder, self).create(vals)
        if record.state == 'sale':
            record._mealshift_send_shipping()
        return record

    def write(self, vals):
        res = super(MealshiftSaleOrder, self).write(vals)
        if 'state' in vals:
            for order in self:
                if order.state == 'sale':
                    order._mealshift_send_shipping()
        return res

    def _mealshift_send_shipping(self):
        if self.state == 'sale' and self.carrier_id.delivery_type == "mealshift":
            configuration_parameters = {
                "id": str(self.carrier_id.id),
                "base_url": self.carrier_id.mealshift_base_url,
                "partner": self.carrier_id.mealshift_partner,
                "ms_partner_id": self.carrier_id.mealshift_ms_partner_id,
                "secret": self.carrier_id.mealshift_secret
            }

            if not configuration_parameters:
                self.write({'mealshift_status_reason': 'No configs found!'})

            for configuration_parameter in configuration_parameters:
                if not configuration_parameters[configuration_parameter] or configuration_parameters[configuration_parameter] == "":
                    self.write({'mealshift_status_reason': 'A config not found!'})


            address_params = [
                self.partner_shipping_id.zip,
                self.partner_shipping_id.country_id.name,
                self.partner_shipping_id.state_id.name if self.partner_shipping_id.state_id else "",
                self.partner_shipping_id.city,
                self.partner_shipping_id.street if self.partner_shipping_id.street else ""
            ]

            for address_param in address_params:
                if not address_param:
                    self.write({'mealshift_status_reason': 'Partner address param missed!'})

            address_str = " ".join(address_params)
            latitude = self.partner_shipping_id.partner_latitude
            longitude = self.partner_shipping_id.partner_longitude
            product_id = self.carrier_id.product_id
            amount = 0
            for line in self.order_line:
                if line.product_id == product_id:
                    amount = line.price_unit * 100

            data = {
                "id": self.name,
                "reference": self.id,
                "clientReference": "w" + str(self.website_id.id),  # should be fetched and detected based on the site id
                "customer": {
                    "name": self.partner_shipping_id.name,
                },
                "payment": {
                    "paymentType": "CARD",
                    # if record.payment_ids[0].payment_method_id.name.lower() == 'cash' else "CARD", # ask how to do it
                    "amount": amount
                },
                "location": {
                    "fullAddress": address_str
                }
            }

            if latitude:
                data['location'].update({'latitude': latitude, 'longitude': longitude})


            mealshift_order_id, mealshift_partner_reference = publish_order(configuration_parameters, data)
            if mealshift_order_id:
                self.write({"mealshift_status": "published", "mealshift_order_id": mealshift_order_id, "mealshift_partner_reference": mealshift_partner_reference})

            else:
                self.write({"mealshift_status_reason": "Error on publishing order"})



    def _action_cancel(self):
        configuration_parameters = {
            "id": str(self.carrier_id.id),
            "base_url": self.carrier_id.mealshift_base_url,
            "partner": self.carrier_id.mealshift_partner,
            "ms_partner_id": self.carrier_id.mealshift_ms_partner_id,
            "secret": self.carrier_id.mealshift_secret
        }

        if not configuration_parameters:
            self.write({'mealshift_status_reason': 'No configs found to cancel!'})

        for configuration_parameter in configuration_parameters:
            if not configuration_parameters[configuration_parameter] or configuration_parameters[
                configuration_parameter] == "":
                self.write({'mealshift_status_reason': 'A config not found to cancel!'})

        data = {
            "clientReference": "w" + str(self.website_id.id),
            "orderReference": self.id
        }

        canceled = cancel_order(configuration_parameters, data)
        if canceled:
            self.write({'mealshift_status': 'canceled'})

        return super(MealshiftSaleOrder, self)._action_cancel()

class MealShiftWebsite(models.Model):
    _inherit = 'website'

    mealshift_client_reference = fields.Char(string="Mealshift Client Reference Name", default="", required=False, compute="_compute_client_reference")

    def _compute_client_reference(self):
        for rec in self:
            rec.mealshift_client_reference = "w" + str(rec.id)
