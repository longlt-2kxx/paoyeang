odoo.define('a1_sale_location.hide_product_print_action', function (require) {
    "use strict";

    const session = require('web.session');
    const core = require('web.core');

    core.bus.on('DOM_updated', null, function () {
        session.user_has_group('a1_sale_location.group_inventory_sales_admin').then(function (isSalesAdmin) {
            if (isSalesAdmin) {
                const actionMenus = document.querySelectorAll('.o_cp_action_menus');
                if (actionMenus.length === 0) {
                    return;
                }

                actionMenus.forEach(function (menu) {
                    menu.style.display = 'none';
                });
            }
        });
    });
});
