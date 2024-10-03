/** @odoo-module */

import { Order } from '@point_of_sale/app/store/models';
import { patch } from "@web/core/utils/patch";


patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.carrier_id = null;
    },
    export_as_JSON() {
        let json = super.export_as_JSON()
        json.carrier_id = this.carrier_id
        console.log("Final JSON: ", json);
        return json;
    }
})