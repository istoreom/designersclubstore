odoo.define('pw_pos_logo_barcode.chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const PosLogo = (Chrome) =>
        class extends Chrome {
            async start() {
                await super.start();
                if (this.env.pos.config.receipt_logo && this.env.pos.config.logo_setting === 'use_company_logo') {
                    var url = window.location.origin + '/web/image?model=res.company&field=logo&id='+this.env.pos.company.id;
                    $('.pos-logo').attr("src", url);
                }
                if (this.env.pos.config.receipt_logo && this.env.pos.config.logo_setting === 'use_pos_logo') {
                    var url = window.location.origin + '/web/image?model=pos.config&field=pos_logo&id='+this.env.pos.config.id;
                    $('.pos-logo').attr("src", url);
                }
            }
        };

    Registries.Component.extend(Chrome, PosLogo);

    return Chrome;
});
