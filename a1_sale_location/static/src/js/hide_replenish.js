odoo.define('a1_sale_location.hide_replenish', function (require) {
    "use strict";
    var session = require('web.session');
    // Đảm bảo code chạy sau khi DOM đã được ready
    var core = require('web.core');
     console.log("🍺 hide_replenish.js loaded");
    // Không chỉ DOM_ready, mà mỗi lần Odoo cập nhật DOM
    core.bus.on('DOM_updated', null, function () {
        // session.user_has_group trả về Promise
        session.user_has_group('a1_sale_location.group_inventory_sales_admin').then(function (isSalesRep) {
            console.log("isSalesRep =", isSalesRep);
            if (isSalesRep) {
                var buttons = document.querySelectorAll('.o_report_replenish_buy');
                console.log("Found", buttons.length, "replenish buttons");
                buttons.forEach(function (btn) {
                    btn.style.display = 'none';
                });
                console.log("Replenish buttons hidden");
            }
        });
    });
});
