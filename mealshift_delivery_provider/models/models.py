# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class mealshift_delivery_provider(models.Model):
#     _name = 'mealshift_delivery_provider.mealshift_delivery_provider'
#     _description = 'mealshift_delivery_provider.mealshift_delivery_provider'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
