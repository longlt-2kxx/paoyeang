odoo.define('a1_sale_location.hide_forecast_icon', function (require) {
    "use strict";
    const session = require('web.session');
    const core = require('web.core');

    core.bus.on('DOM_updated', null, function () {
        session.user_has_group('sales_team.group_sale_manager').then(function (isManager) {
            if (!isManager) {
                document.body.classList.add('hide-forecast-icon');

                // Ẩn trực tiếp icon nếu CSS chưa hiệu quả
                document.querySelectorAll('a.fa-area-chart').forEach(function (icon) {
                    icon.style.display = 'none';
                });
            }
        });
    });
});
