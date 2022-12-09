# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Website Thawani Checkout Payment Acquirer",
  "summary"              :  """Website Thawani Checkout Payment Acquirer integrates Thawani with your Odoo for accepting quick payments from customers.""",
  "category"             :  "Website",
  "version"              :  "1.0.4",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",
  "description"          :  """Website Thawani Checkout Payment Acquirer""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_thawani_checkout",
  "depends"              :  ['payment'],
  "data"                 :  [
                             'views/thawani_checkout_template.xml',
                             'views/thawani_acquirer_view.xml',
                             'data/thawani_checkout_demo_data.xml',
                            ],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  149,
  "images"               :  ['static/description/Banner.gif'],
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
