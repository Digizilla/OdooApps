from odoo import _, api, models
import logging
from markupsafe import Markup

_logger = logging.getLogger(__name__)
# from odoo.addons.iap.tools import iap_tools

DEFAULT_ENDPOINT = 'https://iap-sms.odoo.com'
APP_ID = ""
APP_SEC = ""

class JawalaySmsApi(models.AbstractModel):
    _inherit = "sms.api"

    @api.model
    def _send_sms_batch(self, messages):
        message = messages[0]['content']
        phone_numbers_with_spaces = [message['number'].split(" ") for message in messages]
        phone_numbers = ["".join(phone_number) for phone_number in phone_numbers_with_spaces]
        _logger.info("PHone nujmbers: ")
        _logger.info(phone_numbers)
        phone_numbers1 = [message['number'] for message in messages]
        _logger.info(phone_numbers1)
        # client = Client("qrQbEGfn6fdESZKUpqiAdZTsrwC4H3oyXUhwl4g7",
        #                 "FAE1IGiKXZO4Sz5Z8dRcgQzSHK0vdSIQqb5WkzyxJ0pUdwMApmTFpfewLR2PBOju27DJ2p95JqDL1bo5hrK4EoWr83yd2aeeBB8J")
        jawaly_app_id = self.env['ir.config_parameter'].sudo().get_param('jawaly_app_id')
        jawaly_app_secret = self.env['ir.config_parameter'].sudo().get_param('jawaly_app_secret')
        _logger.info("app id")
        _logger.info(jawaly_app_id)
        _logger.info("app secret")
        _logger.info(jawaly_app_secret)
        jawaly_sender_id = self.env['ir.config_parameter'].sudo().get_param('jawaly_sender')
        jawaly_sender = self.env['jawaly.sender.names'].browse(int(jawaly_sender_id))
        jawaly_sender_name = jawaly_sender.name if jawaly_sender else '4jawaly'
        _logger.info("jawaly sender name1")
        _logger.info(jawaly_sender_name)
        # jawaly_sender_name = "4jawaly"
        # client = Client("aFj4pMudVW1uEaQrUaK3a3k0d6YNjufg2M2WAdgm",
        #                 "hWMzJWk1HpyIK5L1j2NgXsTD0USYVlXDuIBgTzMGCU5eM8tCkw8oY0UbxOxsMYlKxdGEWofXjsZer1cSOdp88QrQayTSNxmwMzmh")
        client = Client(jawaly_app_id, jawaly_app_secret)
        response = client.send_message(message, phone_numbers, jawaly_sender_name)
        _logger.info("Response")
        _logger.info(response)
        params = {
            'messages': messages
        }
        contact_iap = self._contact_iap('/iap/sms/2/send', params)
        log = self.env['jawaly.log'].sudo().create({
            'number': phone_numbers,
            'description': message,
            'log': response,
        })
        bootstrap_cls, title, content = ("success", _("Message Sent Successfully"), "")

        if response['code'] != 200:
            bootstrap_cls, title = ("danger", _("Message Delivery Failed"))
            content = Markup("""
                <p class='mb-0'>
                    %s
                </p>
                <hr>
                <p class='mb-0'>
                    %s
                </p>
            """) % (_('The message could not be delivered. Please check the response below:'), response['message'])

        for message in messages:
            model = self.env['sms.sms'].browse(message['res_id']).mail_message_id.model
            id = self.env['sms.sms'].browse(message['res_id']).mail_message_id.res_id
            record = self.env[model].browse(id)
            message_post = record.message_post(
                body=Markup("""
                <div role='alert' class='alert alert-%s'>
                    <h4 class='alert-heading'>%s</h4>%s
                </div>
            """) % (bootstrap_cls, title, content))
            print('$$$$$$$$$$$$$$$$$', message_post)

        return contact_iap

    @api.model
    def _contact_iap(self, local_endpoint, params):
        res = super(JawalaySmsApi, self)._contact_iap(local_endpoint, params)
        return res


import base64
import requests
import json


class Client:
    def __init__(self, app_id, app_sec):
        self.app_id = app_id
        self.app_sec = app_sec
        self.base_url = "https://api-sms.4jawaly.com/api/v1/"
        self.app_hash = base64.b64encode(f"{app_id}:{app_sec}".encode()).decode()

    def get_packages(self, **kwargs):
        query = {
            "is_active": 1,
            "order_by": "id",
            "order_by_type": "desc",
            "page": 1,
            "page_size": 10,
            "return_collection": 1
        }
        query.update(kwargs)
        url = f"{self.base_url}account/area/me/packages?{query}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.app_hash}"
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def get_senders(self, **kwargs):
        query = {
            "page_size": 10,
            "page": 1,
            "status": 1,
            "sender_name": "",
            "is_ad": "",
            "return_collection": 1
        }
        query.update(kwargs)
        url = f"{self.base_url}account/area/senders?{query}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.app_hash}"
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def send_message(self, text, numbers, sender):
        messages = {"messages": [{"text": text, "numbers": numbers, "sender": sender}]}
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.app_hash}'
        }
        url = f'{self.base_url}account/area/sms/send'
        response = requests.post(url, headers=headers, json=messages)
        return response.json()