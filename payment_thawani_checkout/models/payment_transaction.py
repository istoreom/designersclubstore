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
import pprint
import logging
import requests
import json

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from werkzeug import urls

_logger = logging.getLogger(__name__)

class TransactionThawaniCheckout(models.Model):
    _inherit = 'payment.transaction'

    def get_thawani_default_currency(self):
        return self.env["res.currency"].sudo().search([('name','=','OMR'),'|',('active','=',True),('active','!=',True)], limit=1)

    def thawani_checkout_create_session(self, processing_values, **post):
        acquirer_id = self.provider_id
        partner_id = self.partner_id
        from_currency = self.currency_id
        to_currency = self.get_thawani_default_currency()

        amount = processing_values.get('amount')
        reference = processing_values.get('reference')
        if acquirer_id and amount:
            if from_currency.id != to_currency.id:
                amount = from_currency._convert(amount, to_currency, self.company_id, fields.Date.today())
            base_url = acquirer_id.get_base_url()
            thawani_base_url = acquirer_id.get_thawani_checkout_base_url()
            header = {
                "Content-Type" : "application/json",
                "thawani-api-key" : acquirer_id.thawani_secret_key,
            }
            products = [{
                "name": reference,
                "unit_amount": int(amount*1000),
                "quantity": 1
            }]
            data = {
                "client_reference_id": reference,
                "products": products,
                "success_url": urls.url_join(base_url, "/payment/thawani_checkout/success?reference=%s" % reference),
                "cancel_url": urls.url_join(base_url, "/payment/thawani_checkout/cancel?reference=%s" % reference),
                "metadata": {
                    "user name": partner_id.name,
                    "user email": partner_id.email,
                    "user mobile": partner_id.mobile,
                },
            }
            data = json.dumps(data)
            url = urls.url_join(thawani_base_url, "/api/v1/checkout/session")
            response = requests.post(url, data=data, headers=header)
            res_data = response.json()
            if res_data:
                if res_data.get('data'):
                    session_id = res_data['data']['session_id'] if res_data['data'].get('session_id') else None
                    if session_id:
                        redirect_url = urls.url_join(thawani_base_url, "/pay/%s" % session_id)
                        return {'secret_key': acquirer_id.thawani_public_key, 'redirect_url': redirect_url}
                elif res_data.get('status') and res_data['status'] == 401:
                    raise UserError(_(res_data.get('detail', 'Something went wrong with Thawani Payment Gateway.')))
                    # return {'status': 'Failed', 'error_msg': res_data.get('detail', 'Something went wrong with Thawani Payment Gateway.')}
        raise UserError(_('Something went wrong with Thawani Payment Gateway.'))
        # return {'status': 'Failed', 'error_msg': 'Something went wrong with Thawani Payment Gateway.'}

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'thawani_checkout':
            return res
        return self.thawani_checkout_create_session(processing_values)

    @api.model
    def _get_tx_from_feedback_data(self,provider, data):
        """ Given a data dict coming from thawani, verify it and find the related
        transaction record. Create a payment method if an alias is returned."""
        res = super()._get_tx_from_feedback_data(provider,data)
        if provider != "thawani_checkout":
            return res
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency')
        tx_ids = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'received data for reference %s' % (pprint.pformat(reference))
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx_ids[0]

    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != "thawani_checkout":
            return
        trans_state = data.get("state", False)
        if trans_state:
            self.write({
                'provider_reference': data.get('provider_reference'),
                'state_message': _("Thawani Payment Gateway Response :-") + data["state"]
            })
            if trans_state == 'paid':
                self._set_done()
            elif trans_state == 'pending':
                self._set_pending()
            elif trans_state == 'cancel':
                self._set_canceled()
