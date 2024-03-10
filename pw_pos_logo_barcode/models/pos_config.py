# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    receipt_logo = fields.Boolean('Logo and Barcode')
    logo_setting = fields.Selection([
        ('use_company_logo', 'Use Company Logo'),
        ('use_pos_logo', 'Use Other Logo')], default='use_company_logo')
    logo = fields.Binary(related='company_id.logo', string="Company Logo")
    pw_pos_logo = fields.Binary(string="POS Logo", store=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    receipt_logo = fields.Boolean('Logo and Barcode', related="pos_config_id.receipt_logo", readonly=False)
    logo_setting = fields.Selection([
        ('use_company_logo', 'Use Company Logo'),
        ('use_pos_logo', 'Use Other Logo')], related="pos_config_id.logo_setting", readonly=False)
    logo = fields.Binary(string="Company Logo", related="company_id.logo", readonly=False)
    pw_pos_logo = fields.Binary(string="POS Logo", related="pos_config_id.pw_pos_logo", readonly=False)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_company(self):
        res = super(PosSession, self)._loader_params_res_company()
        fields = res.get('search_params').get('fields')
        if fields:
            fields += ['street', 'city', 'zip']
            res['search_params']['fields'] = fields
        return res
