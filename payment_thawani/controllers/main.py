# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ThawaniController(http.Controller):

    @http.route(['/payment/thawani/return', '/payment/thawani/cancel',
                 ], type='http', auth='public', csrf=False)
    def thawani_form_feedback(self, **post):
        """ THAWANI."""
        _logger.info(
            'Thawani: entering form_feedback with post data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo()._handle_feedback_data('thawani', post)

        return request.redirect('/payment/status')

