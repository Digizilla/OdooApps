from odoo import models, fields, api


class JawalyLogs(models.Model):
    _name = 'jawaly.log'
    _rec_name = 'number'
    _order = 'id desc'
    number = fields.Char(string='Number')
    description = fields.Text(string='Message')
    log = fields.Text(string='log')