/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
    },
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result['headerData']['receipt_logo'] = this.pos.config.receipt_logo;
        result['headerData']['logo_setting'] = this.pos.config.logo_setting;
        result['headerData']['config_id'] = this.pos.config.id;
        var canvas = document.createElement('canvas');
        JsBarcode(canvas, result.name);
        result['receipt_logo'] = this.pos.config.receipt_logo;
        result['pw_barcode'] = canvas.toDataURL("image/png");
        return result;
    },
});
