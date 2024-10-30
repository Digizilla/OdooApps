from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SmsSenderComposer(models.TransientModel):
    _inherit = 'sms.composer'

    def action_send_sms(self):
        print("this send have been clicked from the inherited model")
        super(SmsSenderComposer, self).action_send_sms()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }