odoo.define('a1_sale_location.hide_replenish', function (require) {
    "use strict";
    var session = require('web.session');
    var core = require('web.core');

    core.bus.on('DOM_updated', null, function () {
        session.user_has_group('a1_sale_location.group_inventory_sales_admin').then(function (isSalesRep) {
            if (isSalesRep) {
                var buttons = document.querySelectorAll('.o_report_replenish_buy');
                buttons.forEach(function (btn) {
                    btn.style.display = 'none';
                });
            }
        });
    });
});
