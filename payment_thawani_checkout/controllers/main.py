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
import werkzeug
import json
import pprint
import odoo

from odoo import http, _
from odoo.http import request, Response
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

_logger = logging.getLogger(__name__)

class ThawaniCheckout(http.Controller):

    @http.route('/payment/thawani_checkout/success', type='http', auth="public", csrf=False, website=True)
    def thawani_checkout_success(self, reference, **post):
        params = {
            "reference" : reference,
            "state" : "pending"
        }
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('thawani_checkout', params)
        tx_sudo._handle_notification_data('thawani_checkout', params)
        return werkzeug.utils.redirect('/payment/status')

    @http.route('/payment/thawani_checkout/cancel', type='http', auth="public", website=True)
    def thawani_checkout_cancel(self, reference, **post):
        params = {
            "reference" : reference,
            "state" : "cancel"
        }
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('thawani_checkout', params)
        tx_sudo._handle_notification_data('thawani_checkout', params)
        return werkzeug.utils.redirect('/payment/status')

    @http.route('/thawani/checkout/webhook/interface', type='json', auth='public')
    def thawani_checkout_webhook_interface(self, **post):
        payload = {}
        if request.httprequest.data:
            payload = json.loads(request.httprequest.data)
            _logger.info("Thawani Checkout Webhook Post Data:\n%s", pprint.pformat(payload))
            data = payload.get('data')
            if data and data.get('client_reference_id'):
                params = {
                    "amount" : data.get('total_amount'),
                    "currency" : data.get('currency'),
                    "reference" : data.get('client_reference_id'),
                    "state" : data.get('payment_status'),
                    "provider_reference" : data.get('invoice'),
                    "session_id" : data.get('session_id'),
                }
                tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('thawani_checkout',params)
                tx_sudo._handle_notification_data('thawani_checkout', params)
        return Response('success', status=200)
