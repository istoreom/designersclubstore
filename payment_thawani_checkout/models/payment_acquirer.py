# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class PaymentProvier(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('thawani_checkout', 'Thawani Checkout')],ondelete={'thawani_checkout': 'cascade'})
    thawani_secret_key = fields.Char("Secret Key", required_if_provider='thawani_checkout', help="Enter thawani secret key.")
    thawani_public_key = fields.Char("Public Key", required_if_provider='thawani_checkout', help="Enter thawani public key.")

    def _get_default_payment_method_id(self, code):
        self.ensure_one()
        if code != 'thawani_checkout':
            return super()._get_default_payment_method_id(code)
        return self.env.ref('payment_thawani_checkout.payment_method_thawani_checkout').id

    def get_thawani_checkout_base_url(self):
        self.ensure_one()
        return "https://checkout.thawani.om" if self.state == 'enabled' else "https://uatcheckout.thawani.om"
