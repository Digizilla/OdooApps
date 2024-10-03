from odoo import api, models, fields, _

class DeliveryMethodsPosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _pos_ui_models_to_load(self):
        models_to_load = super(DeliveryMethodsPosSession, self)._pos_ui_models_to_load()

        models_to_load += ['delivery.carrier']
        return models_to_load

    def _loader_params_delivery_carrier(self):
        return {
            'search_params': {
                'domain': [('published_on_pos', '=', True)],
                'fields': ['id', 'name', 'product_id', 'product_barcode', 'delivery_type']
            }
        }

    def _get_pos_ui_delivery_carrier(self, params):
        return self.env['delivery.carrier'].search_read(**params['search_params'])


