# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import requests
import json
import pprint
import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirerThawani(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('thawani', 'Thawani')], ondelete={'thawani': 'set default'})
    thawani_secret_key = fields.Char(string='Secret API Key', required_if_provider='thawani', groups='base.group_user')
    thawani_publishable_key = fields.Char(string='Publishable Key', required_if_provider='thawani', groups='base.group_user')
    session_id = fields.Char(string="Session ID")
    thawani_payment_url = fields.Char(string='Payment URL', required_if_provider='thawani', groups='base.group_user')

    tx_url = ""

    @api.onchange('state')
    def onchange_payment_state(self):
        if self.state == 'enabled':
            self.thawani_payment_url = 'https://checkout.thawani.om'
        else:
            self.thawani_payment_url = 'https://uatcheckout.thawani.om'

    def _get_thawani_urls(self, environment):
        """ THAWANI URLs"""
        thawani_url = "{server_url}/pay/{session_id}?key={pub_key}".format(server_url=self.thawani_payment_url, session_id=self.session_id, pub_key=self.thawani_publishable_key)
        return {'thawani_form_url': thawani_url}

    def create_charge(self, values):
        url = self.thawani_payment_url + "/api/v1/checkout/session"
        headers = {
            'Content-Type': "application/json",
            'thawani-api-key': self.thawani_secret_key
        }
        sale_order = self.env['sale.order'].sudo().search([('name', '=', values.get('reference').split('-')[0])])
        product_list = []
        omr_currency_id = self.env.ref('base.OMR')
        sale_currency_id = sale_order.currency_id
        for line in sale_order.order_line:
            if line.price_total and line.product_uom_qty:
                unit_amount = (line.price_total / line.product_uom_qty) if line.product_uom_qty else line.price_unit
                if sale_currency_id != omr_currency_id:
                    unit_amount = line.currency_id._convert(unit_amount, omr_currency_id, sale_order.company_id or self.env.company, fields.Date.today())
                product_list.append({
                    "name": line.product_id.name,
                    "quantity": int(line.product_uom_qty),
                    "unit_amount": int(unit_amount * 1000)
                })
        payload = {
            "client_reference_id": str(values.get('partner_id')),
            "mode": "payment",
            "products": product_list,
            "success_url": self.return_post_data(),
            "cancel_url": self.return_redirect_thawani_url(),
            "metadata": {
                "Customer name": values.get('partner_name') or sale_order.partner_id.name,
                "order id": sale_order.id,
                "reference": values.get('reference'),
                "thawani_id": self.id,
            }
        }
        # "src_all""src_kw.knet"
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        response_dict = json.loads(response.text)
        _logger.info('Thawani PAYMENT: RESPONSE %s' % response_dict)
        return response_dict

    def thawani_form_generate_values(self, values):
        self.ensure_one()
        thawani_values = self.create_charge(values)
        if thawani_values.get('success') == True:
            url = "{server_url}/pay/{session_id}?key={pub_key}".format(server_url=self.thawani_payment_url,session_id=thawani_values.get('data').get('session_id'), pub_key=self.thawani_publishable_key)
            self.session_id = thawani_values.get('data').get('session_id')
            url_update = self._get_thawani_urls(self.state)
            url_update.update({
                'thawani_form_url': url
            })
            values.update({
                'tx_url': url,
                'api_url': url,
                "success_url": self.return_post_data(),
                "currency": self.env.ref('base.OMR').id,
                "return_url": self.return_redirect_thawani_url(),
                'thawani_publishable_key': self.thawani_publishable_key
            })
            return values
        else:
            raise ValidationError(_("No any session created for current order."))

    def return_customer_details(self,values):
        res = {
            'first_name': values.get('partner_first_name'),
            'last_name': values.get('partner_last_name'),
            'email': values.get('partner_email'),
            'phone': {'number': values.get('partner_phone')},
        }
        return res

    def return_post_data(self):
        base_url = self.get_base_url()
        return urls.url_join(base_url, '/payment/thawani/return')

    def return_redirect_thawani_url(self):
        base_url = self.get_base_url()
        return urls.url_join(base_url, '/payment/thawani/return')

    def thawani_get_form_action_url(self):
        self.ensure_one()
        if self.tx_url:
            return self.tx_url
        else:
            return self._get_thawani_urls(self.state)['thawani_form_url']

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'thawani':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_thawani.payment_method_thawani').id


class ThawaniPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def retrive_charge(self, thawani_id):
        thawani = self.env['payment.acquirer'].search([('provider', '=', 'thawani')], limit=1)
        url = "%s/api/v1/checkout/session/%s" % (thawani.thawani_payment_url, thawani.session_id)
        headers = {
            'thawani-api-key': thawani.thawani_secret_key
        }
        response = requests.request("GET", url, headers=headers)
        response_dict = json.loads(response.text)
        _logger.info('Thawani PAYMENT: retrive_charge %s' % response_dict)
        return response_dict

    @api.model
    def _thawani_form_get_tx_from_data(self, data):
        retrive = self.retrive_charge(data.get('thawani_id'))
        if retrive.get('success') == True:
            reference = retrive.get('data').get('metadata').get('reference') #, amount, currency_name data.get('amount'), data.get('currency_name')
            tx = self.search([('reference', '=', reference)])
            if not tx or len(tx) > 1:
                error_msg = _('received data for reference %s') % (pprint.pformat(reference))
                if not tx:
                    error_msg += _('; no order found')
                else:
                    error_msg += _('; multiple order found')
                _logger.info(error_msg)
                raise ValidationError(error_msg)
        else:
            raise ValidationError(_('Error'))
        return tx.with_context(transaction_data=retrive)

    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != 'thawani':
            return
        if self._context.get('transaction_data'):
            reference = self._context.get('transaction_data')
        else:
            reference = self.retrive_charge(data.get('thawani_id'))
        if reference.get('success') == True and reference.get('data').get('payment_status') == 'paid':
            res = {
                'acquirer_reference': reference.get('data').get('metadata').get('thawani_id'),
            }
            self.write(res)
            self._set_done()
        else:
            error = 'Received status %s from Thawani Payment Gateway For : %s, so this transaction will be considered as cancelled' % (reference.get('data').get('payment_status'), self.reference,)
            res = {
                'acquirer_reference': data.get('thawani_id'),
            }
            res.update(state_message=error)
            self.write(res)
            self._set_canceled()

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Paypal-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'thawani':
            return res
        res = self.acquirer_id.thawani_form_generate_values(processing_values)
        return res

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Find the transaction based on the feedback data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the acquirer
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'thawani':
            return tx
        tx = self._thawani_form_get_tx_from_data(data)
        return tx
