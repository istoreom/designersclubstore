odoo.define('pw_pos_logo_barcode.models', function (require) {
    "use strict";

    const { Order} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosChangeLogo = (Order) => class PosChangeLogo extends Order {
        export_for_printing() {
            var receipt = super.export_for_printing(...arguments);
            var canvas = document.createElement('canvas');
            JsBarcode(canvas, receipt['name']);
            if (this.pos.config.receipt_logo){
                receipt['pw_pos_logo'] = 'data:image/png;base64,' + this.pos.config.pw_pos_logo;
                receipt['barcode'] = canvas.toDataURL("image/png");
            }
            receipt.company.state_id = this.pos.company.state_id;
            receipt.company.zip = this.pos.company.zip;
            receipt.company.street = this.pos.company.street;
            receipt.company.city = this.pos.company.city;
            return receipt;
        }
    }
    Registries.Model.extend(Order, PosChangeLogo);
});
