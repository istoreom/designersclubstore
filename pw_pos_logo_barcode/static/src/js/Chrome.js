/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";

patch(Navbar.prototype, {
    setup() {
        super.setup(...arguments);
    },
    get imageUrl() {
        if (this.pos.config.receipt_logo && this.pos.config.logo_setting === 'use_company_logo') {
            return `/web/image?model=res.company&field=logo&id=${this.pos.company.id}`;
        }
        if (this.pos.config.receipt_logo && this.pos.config.logo_setting === 'use_pos_logo') {
            return `/web/image?model=pos.config&field=pw_pos_logo&id=${this.pos.config.id}&unique=${this.pos.config.write_date}`;
        }
    }
});
