/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_coupon.pos_coupon', function(require) {
    "use strict";
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var utils = require('web.utils');
    var rpc = require('web.rpc');
    var round_di = utils.round_decimals;
    var QWeb = core.qweb;
    var SuperPosModel = models.PosModel.prototype;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');

    models.load_fields('res.users', 'allow_coupon_create');

    class CreateconfirmPopupWidget extends AbstractAwaitablePopup {
        click_print_coupons(event){
            var self = this;
            var currentOrder = self.env.pos.get('selectedOrder');
            if (self.env.pos.config.iface_print_via_proxy) {
                        rpc.query({
                        model: 'voucher.voucher',
                        method: 'get_coupon_data',
                        args : [
                            self.props.wk_id],
                            })
                        .then(function(result){
                            var receipt = currentOrder.export_for_printing();
                            receipt['coupon'] = result;
                            var t = QWeb.render('CouponXmlReceipt', {
                                receipt: receipt,
                                widget: self,
                            });
                            self.env.pos.proxy.printer.print_receipt(t);
                        });

            } else {
                    self.env.pos.do_action('wk_coupons.coupons_report',{
                        additional_context:{
                            active_ids: [self.props.wk_id],
                        }
                    });
                    self.cancel();
            }
        }
    }
    CreateconfirmPopupWidget.template = 'CreateconfirmPopupWidget';
    CreateconfirmPopupWidget.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(CreateconfirmPopupWidget);

    class CreateCouponPopupWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            var self = this;
            rpc.query({
                model: 'voucher.voucher',
                method: 'get_default_values',
            })
            .then(function(result){
                self.props.wk_coupon_product_id = result.product_id;
                self.props.max_expiry_date = result.max_expiry_date;
                self.props.min_amount = result.min_amount;
                self.props.max_amount = result.max_amount;
                if(result.product_id != null)
                {
                    $("input[name=wk_coupon_validity]").val(result.default_validity);
                    $("input[name=wk_coupon_availability]").val(result.default_availability);
                    $("input[name=wk_coupon_value]").val(result.default_value);
                    $("select[name=wk_customer_type]").val(result.customer_type);
                    $("input[name=wk_redeemption_limit]").val(result.partial_limit);
                    $("input[name=wk_coupon_name]").val(result.wk_coupon_name);
                    $("#wk_partial_redeemed").attr('checked', result.partially_use);
                }
                self.change_customer_type();
            });
        }
        saveBackend(name, validity, availability, coupon_value, note, customer_type, partner_id, voucher_usage, amount_type, max_expiry_date, redeemption_limit, partial_redeem){
            var self = this;
            rpc.query({
                model: 'voucher.voucher',
                method: 'create_coupons',
                args: [{
                    'name': name,
                    'validity': validity,
                    'total_available': availability,
                    'coupon_value': coupon_value,
                    'note': note,
                    'customer_type': customer_type,
                    'partner_id': partner_id,
                    'voucher_usage': voucher_usage,
                    'amount_type': amount_type,
                    'max_expiry_date': max_expiry_date,
                    'redeemption_limit': redeemption_limit,
                    'partial_redeem': partial_redeem
                }],
            })
            .then(function(result){
                self.showPopup('CreateconfirmPopupWidget', {
                        'wk_id': result,
                });
            });
        }
        change_customer_type(event){
            if ($("select[name=wk_customer_type]").val() == 'special_customer') {
                $("input[name=wk_coupon_availability]").parent().hide();
                $("#wk_partial_redeemed").parent().parent().parent().show();
            } else {
                $("input[name=wk_coupon_availability]").parent().show();
                $("#wk_partial_redeemed").parent().parent().parent().hide();
            }
        }
        click_wk_create_coupon(event){
            var self = this;
            function isNumber(o) {
                return !isNaN(o - 0) && o !== null && o !== "" && o !== false;
            }
            var order = self.env.pos.get('selectedOrder');
            if (self.props.wk_coupon_product_id == null) {
                self.showPopup('ErrorPopup', {
                    title: self.env._t('Error !!!'),
                    body: self.env._t('Coupon Configuration is Required'),
                });
            } else {
                $("select[name=wk_partner_id]").removeClass("wk_text_error");
                $('.wk_valid_error').html("");
                var name = $("input[name=wk_coupon_name]").removeClass("wk_text_error").val();
                var validity = $("input[name=wk_coupon_validity]").removeClass("wk_text_error").val();
                var availability = $("input[name=wk_coupon_availability]").removeClass("wk_text_error").val();
                var coupon_value = $("input[name=wk_coupon_value]").removeClass("wk_text_error").val();
                var note = $("textarea[name=note]").val();
                var customer_type = $("select[name=wk_customer_type]").removeClass("wk_text_error").val();
                var voucher_usage = $("select[name=wk_coupon_usage]").removeClass("wk_text_error").val();
                var redeemption_limit = $("input[name=wk_redeemption_limit]").removeClass("wk_text_error").val();
                var partial_redeem = $("#wk_partial_redeemed").is(":checked");
                var amount_type = $("select[name=wk_amount_type]").removeClass("wk_text_error").val();
                var max_expiry_date = self.props.max_expiry_date;
                var min_amount = self.props.min_amount;
                var max_amount = self.props.max_amount;
                if (name != '') {
                    if (isNumber(validity)) {
                        if (validity!=0) {
                            if (isNumber(availability) && availability != 0) {
                                if (isNumber(coupon_value) && coupon_value != 0) {
                                    if (!(amount_type == 'percent' && (coupon_value < 0 || coupon_value > 100))) {
                                        if (parseInt(coupon_value) >= min_amount && parseInt(coupon_value) <= max_amount) {
                                            if (customer_type == 'special_customer') {
                                                if (order.get_client() == null) {
                                                    self.showPopup('ErrorPopup', {
                                                        title: self.env._t('Error !!!'),
                                                        body: self.env._t('Please Select Customer!!!!'),
                                                    });
                                                } else {
                                                    if (partial_redeem == true) {
                                                        if (redeemption_limit == 0){
                                                            $("input[name=wk_redeemption_limit]").addClass("wk_text_error");
                                                            $("input[name=wk_redeemption_limit]").parent().find('.wk_valid_error').html("This field is required & should not be 0");
                                                        }
                                                        else {
                                                            self.saveBackend(name, validity, availability, coupon_value, note, customer_type, order.get_client().id, voucher_usage, amount_type, max_expiry_date, redeemption_limit, partial_redeem);
                                                        }
                
                                                    } else
                                                        self.saveBackend(name, validity, availability, coupon_value, note, customer_type, order.get_client().id, voucher_usage, amount_type, max_expiry_date, -1, false);
                                                }
                                            } else{
                                                self.saveBackend(name, validity, availability, coupon_value, note, customer_type, false, voucher_usage, amount_type, max_expiry_date, -1, false);
                                            }
                                        } else {
                                            if (parseInt(coupon_value) < min_amount)
                                                $("input[name=wk_coupon_value]").parent().find('.wk_valid_error').html("(Min. allowed value is " + min_amount + ")");
                                            else
                                                $("input[name=wk_coupon_value]").parent().find('.wk_valid_error').html("(Max. allowed value is " + max_amount + ")");
                                        }
                                    } else {
                                        $("input[name=wk_coupon_value]").parent().find('.wk_valid_error').html("Must be > 0 & <=100");
                                    }
                                } else {
                                    $("input[name=wk_coupon_value]").addClass("wk_text_error");
                                    $("input[name=wk_coupon_value]").parent().find('.wk_valid_error').html("Value should be >0");
                                }
                            } else {
                                $("input[name=wk_coupon_availability]").addClass("wk_text_error");
                                $("input[name=wk_coupon_availability]").parent().find('.wk_valid_error').html("Availability can't be 0");
                            }
                        }else{
                            $("input[name=wk_coupon_validity]").addClass("wk_text_error");
                            $("input[name=wk_coupon_validity]").parent().find('.wk_valid_error').html("Validity can't be 0");
                        }
                    } else
                        $("input[name=wk_coupon_validity]").addClass("wk_text_error");
                } else
                    $("input[name=wk_coupon_name]").addClass("wk_text_error");
            }
        }
    }
    CreateCouponPopupWidget.template = 'CreateCouponPopupWidget';
    CreateCouponPopupWidget.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(CreateCouponPopupWidget);

    class RedeemPopupRetryWidget extends AbstractAwaitablePopup {
        mounted() {
            this.playSound('error');
        }
        click_wk_retry_coupons(event){
            this.showPopup('RedeemPopupWidget');
        }
    }
    RedeemPopupRetryWidget.template = 'RedeemPopupRetryWidget';
    RedeemPopupRetryWidget.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(RedeemPopupRetryWidget);

    class RedeemPopupValidateWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            var self = this;
            self.props.wk_product_id = self.props.wk_product_id;
            self.props.secret_code = self.props.secret_code;
            self.props.total_val = self.props.total_val;
            self.props.coupon_name = self.props.coupon_name;
        }
        click_wk_retry_coupons(event){
            var self = this;
            var selectedOrder = self.env.pos.get('selectedOrder');
            rpc.query({
                model: 'voucher.voucher',
                method: 'redeem_voucher_create_histoy',
                args : [self.props.coupon_name, self.props.secret_code, self.props.total_val, false, false, 'pos'],
                }).then(function(result) {
                    if (result['status']) {
                        selectedOrder.coupon_id = self.props.secret_code;
                        selectedOrder.wk_product_id = self.props.wk_product_id;
                        selectedOrder.wk_voucher_value = self.props.total_val;
                        selectedOrder.history_id = result['history_id'];
                        var product = self.env.pos.db.get_product_by_id(self.props.wk_product_id);
                        var last_orderline = selectedOrder.get_last_orderline();
                        last_orderline.coupon_name = self.props.coupon_name;
                        if (product != undefined) {
                            selectedOrder.add_product(product, {
                                price: -(self.props.total_val)
                            });
                            selectedOrder.get_last_orderline().price_manually_set = true;
                            self.cancel();
                            self.showScreen('ProductScreen')
                        } else {
                            self.showPopup('ErrorPopup', {
                                title: self.env._t('Error !!!'),
                                body: self.env._t('Voucher product not available in POS. Please make the voucher product available in POS'),
                            });
                        }
                    }
                }).catch(function(unused, event) {
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Error !!!'),
                        body: self.env._t('Connection Error. Try again later !!!!'),
                    });
            });

        }
    }
    RedeemPopupValidateWidget.template = 'RedeemPopupValidateWidget';
    RedeemPopupValidateWidget.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(RedeemPopupValidateWidget);

    class RedeemPopupWidget extends AbstractAwaitablePopup {
        click_wk_redeem_coupons(event) {
            var self = this;
            var order = self.env.pos.get('selectedOrder');
            if (order == null) {
                return false;
            }
            var orderlines = order.orderlines;
            var coupon_product = true;
            var prod_list = []
            var selected_prod_percent_price = 0
            for (var i = 0; i < orderlines.models.length; i++) {
                prod_list.push(orderlines.models[i].product.id);
            }
            var secret_code = $("#coupon_8d_code").val();
            rpc.query({
                model: 'voucher.voucher',
                method: 'validate_voucher',
                args :[secret_code, order.get_total_without_tax(), prod_list, 'pos', order.get_client() ? order.get_client().id : 0]
                }).catch(function(unused, event) {
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Error !!!'),
                        body: self.env._t('Connection Error. Try again later !!!!'),
                    });
            }).then(function(result) {
                if (orderlines.models.length) {
                    for (var i = 0; i < orderlines.models.length; i++) {
                        if (orderlines.models[i].product.id == result.product_id)
                            coupon_product = false;
                        if (result.product_ids !== undefined)
                            if ($.inArray(orderlines.models[i].product.product_tmpl_id, result.product_ids) !== -1)
                                selected_prod_percent_price += orderlines.models[i].price * orderlines.models[i].quantity;
                    }
                    if (coupon_product) {
                            if (result.status) {
                                var total_amount = order.get_total_with_tax();
                                var msg;
                                var total_val;
                                var res_value = result.value;
                                if (result.customer_type == 'general') {
                                    if (result.voucher_val_type == 'percent') {
                                        res_value = (total_amount * result.value) / 100;
                                        if (result.applied_on == 'specific')
                                            res_value = (selected_prod_percent_price * result.value) / 100;
                                        else
                                            total_amount = res_value;
                                    } else {
                                        if (result.applied_on == 'specific')
                                            total_amount = selected_prod_percent_price
                                    }
                                } else{
                                    if (result.voucher_val_type == 'percent') {
                                        res_value = (total_amount * result.value) / 100;
                                        if (result.applied_on == 'specific')
                                            res_value = (selected_prod_percent_price * result.value) / 100;
                                        else
                                            total_amount = res_value;
                                    } else {
                                        if (result.applied_on == 'specific')
                                            total_amount = selected_prod_percent_price
                                    }
                                }
                                if (total_amount < res_value) {
                                    msg = total_amount;
                                    total_val = total_amount;
                                } else {
                                    msg = res_value;
                                    total_val = res_value;
                                }
                                msg = parseFloat(round_di(msg, 2).toFixed(2));
                                self.showPopup('RedeemPopupValidateWidget', {
                                    'title': self.env._t(result.message),
                                    'msg': self.env._t(msg),
                                    'wk_product_id': result.product_id,
                                    'secret_code': result.coupon_id,
                                    'total_val': total_val,
                                    'coupon_name': result.coupon_name,
                                    'coupon_code': result.voucher_code,

                                });
                        } else {
                            self.showPopup('RedeemPopupRetryWidget', {
                                'title': self.env._t("Error: " + result.message),
                            });
                        }
                    } else {
                        self.showPopup('ErrorPopup', {
                            title: self.env._t('Error !!!'),
                            body: self.env._t("Sorry, you can't use more than one coupon in single order."),
                        });
                    }
                } else {
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Error !!!'),
                        body: self.env._t('Sorry, there is no product in order line.'),
                    });
                }
            });
        }
    }
    RedeemPopupWidget.template = 'RedeemPopupWidget';
    RedeemPopupWidget.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(RedeemPopupWidget);

    class CouponPopupWidget extends AbstractAwaitablePopup {
        click_gift_coupons_create(product) {
            this.showPopup('CreateCouponPopupWidget');
        }
        click_gift_coupons_redeem(event){
            this.showPopup('RedeemPopupWidget');
            $('#coupon_8d_code').focus();
        }
    }
    CouponPopupWidget.template = 'CouponPopupWidget';
    CouponPopupWidget.defaultProps = {
        title: 'Confirm ?',
        value:''
    };
    Registries.Component.add(CouponPopupWidget);

    class CouponButtonWidget extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {
            this.showPopup('CouponPopupWidget');
        }
    }
    CouponButtonWidget.template = 'CouponButtonWidget';
    Registries.Component.add(CouponButtonWidget);

    ProductScreen.addControlButton({
        component: CouponButtonWidget,
        condition: function() {
            return true;
        },
    });

    var _super = models.Order;
    models.Order = models.Order.extend({
        initialize: function(attributes) {
            this.coupon_id = 0;
            this.wk_product_id = 0;
            this.history_id = 0;
            _super.prototype.initialize.apply(this, arguments);
        },
        export_as_JSON: function() {
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            var order = this.pos.get('selectedOrder');
            if (order != null) {
                var orderlines = order.orderlines;
                var coupon_state = true;
                for (var i = 0; i < orderlines.models.length; i++)
                    if (orderlines.models[i].product.id == order.wk_product_id)
                        coupon_state = false;
                if (coupon_state)
                    json.coupon_id = 0;
                else
                    json.coupon_id = order.coupon_id || 0;
            }
            return json;
        },
    });

    models.PosModel = models.PosModel.extend({
        _save_to_server: function(orders, options) {
            var self = this;
            return SuperPosModel._save_to_server.call(this, orders, options).then(function(server_ids) {
                /*-------------CODE FOR POS VOUCHERS START------*/
                if (server_ids) {
                    var wk_order = self.get_order();
                    if (wk_order != null) {
                        var coupon_id = wk_order.coupon_id;
                        var wk_product_id = wk_order.wk_product_id;
                        var wk_voucher_value = wk_order.wk_voucher_value;
                        for (var i = 0; i < wk_order.orderlines.models.length; i++) {
                            // $('.receipt-screen.screen span.button.next').show();
                            if (wk_order.orderlines.models[i].product.id == wk_product_id) {
                                var client_id = false;
                                if (self.get_client()) {
                                    client_id = self.get_client().id;
                                }

                                if(server_ids.order_ids){
                                    var ids = server_ids.order_ids
                                }
                                else{
                                    var ids = server_ids
                                }

                                rpc.query({
                                    model: 'voucher.voucher',
                                    method: 'pos_create_histoy',
                                    args :  [coupon_id, wk_voucher_value, ids[0], wk_order.orderlines.models[i].id, client_id],
                                    }).catch(function(unused, event) {
                                        self.showPopup('ErrorPopup', {
                                            title: self.env._t('Error !!!'),
                                            body: self.env._t('Connection Error. Try again later !!!'),
                                        });
                                    })
                                    .then(function(result) {
                                    });
                            }
                        }
                    }
                }
                /*-------------CODE FOR POS VOUCHERS END------*/
                return server_ids;
            });
        },
    });

    // Inherit NumpadWidget----------------
    const PosResNumpadWidget = (NumpadWidget) =>
		class extends NumpadWidget {
            sendInput(key) {
                var order = this.env.pos.get_order();
                var p_id = order.get_selected_orderline();
                if (((key == '9') || (key == '8') || (key == '7') || (key == '6') || (key == '5') || (key == '4') || (key == '3') || (key == '2') || (key == '1') || (key == '0')) && order.get_selected_orderline() && (order.wk_product_id === order.get_selected_orderline().product.id)) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Error !!!'),
                        body: this.env._t('You can not change the quantity, discount or price of the applied voucher'),
                    });
                } else {
                    super.sendInput(key);
                }
            }
		};
    Registries.Component.extend(NumpadWidget, PosResNumpadWidget);

//  screens.ReceiptScreenWidget.include({
//         click_next: function() {
//         // $('.receipt-screen.screen span.button.next').hide();
//         this.pos.get_order().finalize();
//     },
//     });

});
