/** @odoo-module */

import { Orderline } from '@point_of_sale/app/store/models';
import { patch } from "@web/core/utils/patch";

console.log("File pos_store.js loaded!!")

patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
        this.delivery_method = null;
    },

})