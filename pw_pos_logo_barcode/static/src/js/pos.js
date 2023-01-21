odoo.define('pw_pos_logo_barcode.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');
models.load_fields('res.company', ['street', 'street', 'city', 'state_id', 'zip']);

var _super_Order = models.Order.prototype;
models.Order = models.Order.extend({
    export_for_printing: function () {
        var res = _super_Order.export_for_printing.apply(this, arguments);
        var canvas = document.createElement('canvas');
        JsBarcode(canvas, res['name']);
        res['barcode'] = canvas.toDataURL("image/png");
        res['pos_logo'] = 'data:image/png;base64,'+this.pos.config.pos_logo;
        return res;
    },
});
});
