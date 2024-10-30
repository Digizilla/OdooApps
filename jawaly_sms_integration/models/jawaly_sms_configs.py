from odoo import models, fields, api
from odoo.exceptions import UserError
from .jawaly_sms_api import Client

class JawalySenderNames(models.Model):
    _name = 'jawaly.sender.names'

    jawaly_id = fields.Integer(string="Jawaly ID", required=True)
    name = fields.Char(string="Sender Name", required=True)
    status = fields.Integer(string="Status", required=True)
    is_ad = fields.Integer(string="Is AD")
    is_default = fields.Integer(string="Is Default")
    jawaly_created_at = fields.Char(string="Jawaly Created At Date")

    @api.model
    def get_senders(self):
        jawaly_app_id = self.env['ir.config_parameter'].sudo().get_param('jawaly_app_id')
        jawaly_app_secret = self.env['ir.config_parameter'].sudo().get_param('jawaly_app_secret')
        client = Client(jawaly_app_id, jawaly_app_secret)

        senders_list = client.get_senders()["items"]["data"]
        for sender in senders_list:
            jawaly_id = sender['id']
            existed_sender = self.search([('jawaly_id', '=', jawaly_id)], limit=1)
            sender_dict = {
                'jawaly_id': jawaly_id,
                'name': sender['sender_name'],
                'status': sender['status'],
                'is_ad': sender['is_ad'],
                'is_default': sender['is_default'],
                'jawaly_created_at': sender['created_at']
            }
            if not existed_sender:
                self.create(sender_dict)
            else:
                existed_sender.write(sender_dict)
        return True

class JawalyResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jawaly_app_id = fields.Char(string="APP ID")
    jawaly_app_secret = fields.Char(string="APP SECRET")
    jawaly_sender_name = fields.Char(string="SENDER NAME")
    jawaly_sender = fields.Many2one('jawaly.sender.names', string="Jawaly Sender OBJ", domain=[('status', '=', 1)])

    @api.model
    def get_values(self):
        res = super(JawalyResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        jawaly_app_id = params.get_param('jawaly_app_id', default='')
        jawaly_app_secret = params.get_param('jawaly_app_secret', default='')
        jawaly_sender_name = params.get_param('jawaly_sender_name', default='')
        jawaly_sender = params.get_param('jawaly_sender', default=False)

        res.update(
            jawaly_app_id=jawaly_app_id,
            jawaly_app_secret=jawaly_app_secret,
            jawaly_sender_name=jawaly_sender_name,
            jawaly_sender=self.env['jawaly.sender.names'].browse(int(jawaly_sender)) if jawaly_sender else False
        )
        return res

    def set_values(self):
        super(JawalyResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("jawaly_app_id", self.jawaly_app_id)
        self.env['ir.config_parameter'].sudo().set_param("jawaly_app_secret", self.jawaly_app_secret)
        self.env['ir.config_parameter'].sudo().set_param("jawaly_sender_name", self.jawaly_sender_name)
        self.env['ir.config_parameter'].sudo().set_param("jawaly_sender", self.jawaly_sender.id if self.jawaly_sender else False)
    def refresh_jawaly_senders(self):
        refreshed = self.env['jawaly.sender.names'].get_senders()
        if not refreshed:
            raise UserError("Couldn't Refresh Senders!!")
        return True