# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class PosConfig(models.Model):
    _inherit = 'pos.config'

    receipt_logo = fields.Boolean('Logo and Barcode')
    logo_setting = fields.Selection([
        ('use_company_logo', 'Use Company Logo'),
        ('use_pos_logo', 'Use Other Logo')], default='use_company_logo')
    logo = fields.Binary(related='company_id.logo', string="Company Logo")
    pos_logo = fields.Binary(string="POS Logo")
