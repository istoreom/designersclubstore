# -*- coding: utf-8 -*-

{
  "name"                 :  "Website Thawani Checkout Payment Acquirer",
  "summary"              :  """Website Thawani Checkout Payment Acquirer integrates Thawani with your Odoo for accepting quick payments from customers.""",
  "category"             :  "Website",
  "version"              :  "17.1",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",
  "description"          :  """Website Thawani Checkout Payment Acquirer""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_thawani_checkout",
  "depends"              :  ['payment','account','website_payment','payment'],
  "data"                 :  [

                             'views/thawani_checkout_template.xml',
                             'views/thawani_acquirer_view.xml',
'data/thawani_checkout_demo_data.xml',


                            ],
  "application"          :  True,
  "installable"          :  True,
  "images"               :  ['static/description/Banner.gif'],
  "currency"             :  "USD",
}
