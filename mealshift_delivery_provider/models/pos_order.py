from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .mealshift_api_methods import publish_order, cancel_order


class MealshiftPosOrder(models.Model):
    _inherit = 'pos.order'

    carrier_id = fields.Many2one('delivery.carrier', required=False, readonly=True)
    mealshift_status = fields.Selection([
        ('not_published', 'Not Published'),
        ('published', 'Published'),
        ('canceled', 'Canceled')
    ],string="Mealshift Status", readonly=True, required=False, default='not_published')
    mealshift_status_reason = fields.Char(string="Mealshift Status Reason", required=False, default="", readonly=True)
    mealshift_order_id = fields.Char(string="Mealshift Order ID", required=False, default="", readonly=True)
    mealshift_partner_reference = fields.Char(string="Mealshift Partner Reference", required=False, defualt="", readonly=True)

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(MealshiftPosOrder, self)._order_fields(ui_order)
        print("Thi sis ui_order: ", ui_order)
        order_fields.update({'carrier_id': ui_order.get('carrier_id', False)})
        return order_fields


    def create(self, vals_list):
        print("POS record vals: ", vals_list)
        record = super(MealshiftPosOrder, self).create(vals_list)
        print("this is vals", vals_list)
        delivery_method = record.carrier_id
        configuration_parameters = {}
        print("this is delivery methodo: ", delivery_method)
        if delivery_method.delivery_type == "mealshift":
            print("entered mealshift")
            configuration_parameters = {
                "id": str(delivery_method.id),
                "base_url": delivery_method.mealshift_base_url,
                "partner": delivery_method.mealshift_partner,
                "ms_partner_id": delivery_method.mealshift_ms_partner_id,
                "secret": delivery_method.mealshift_secret
            }
            if not configuration_parameters:
                record.write({'mealshift_status_reason': 'No configs found!'})
                return record

            for configuration_parameter in configuration_parameters:
                if not configuration_parameters[configuration_parameter] or configuration_parameters[configuration_parameter] == "":
                    record.write({'mealshift_status_reason': 'A config not found!'})
                    return record

            address_params = [
                record.partner_id.zip,
                record.partner_id.country_id.name,
                record.partner_id.state_id.name if record.partner_id.state_id else "",
                record.partner_id.city,
                record.partner_id.street if record.partner_id.street else ""
            ]

            for address_param in address_params:
                if not address_param:
                    record.write({'mealshift_status_reason': 'Partner address param missed!'})
                    return record

            address_str = " ".join(address_params)
            latitude = record.partner_id.partner_latitude
            longitude = record.partner_id.partner_longitude
            product_id = delivery_method.product_id
            amount = 0
            for line in record.lines:
                if line.product_id == product_id:
                    amount = line.price_unit * 100
            data = {
                "id": record.name,
                "reference": record.id,
                "clientReference": "p" + str(record.config_id.id),  # should be fetched and detected based on the site id
                "customer": {
                    "name": record.partner_id.name,
                },
                "payment": {
                    "paymentType": "CASH", # if record.payment_ids[0].payment_method_id.name.lower() == 'cash' else "CARD", # ask how to do it
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
                record.write({"mealshift_status": "published", "mealshift_order_id": mealshift_order_id, "mealshift_partner_reference": mealshift_partner_reference})
                return record

            else:
                record.write({"mealshift_status_reason": "Error on publishing order"})
                return record

        return record

    def cancel_mealshift_order(self):
        if self.carrier_id.delivery_type == "mealshift":
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
                "clientReference": "p" + str(self.config_id.id),
                "orderReference": str(self.id)
            }

            canceled = cancel_order(configuration_parameters, data)
            if canceled:
                self.write({'mealshift_status': 'canceled'})
            else:
                raise UserError("Cannot cancel this order!, this is an order linked with mealshift and an error happened ")

class MealShiftPosConfig(models.Model):
    _inherit = 'pos.config'

    mealshift_client_reference = fields.Char(string="Mealshift Client Reference Name", default="", required=False, compute="_compute_client_reference")

    def _compute_client_reference(self):
        for rec in self:
            rec.mealshift_client_reference = "p" + str(rec.id)