/** @odoo-module */

import { PaymentScreen } from '@point_of_sale/app/screens/payment_screen/payment_screen'
import { Orderline } from '@point_of_sale/app/store/models';
import { patch } from "@web/core/utils/patch";
import { jsonrpc } from "@web/core/network/rpc_service";
import { useState } from "@odoo/owl";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.delivery_methods = this.pos.delivery_methods;
        this.state = useState({
            'delivery_methods_info': this.getDeliveryMethodsSetupInfo()
        });

        this.updateDeliveryMethodsInfo()

        this.checkDeliveryOrderLine()
    },

    async selectPartner(isEditMode = false, missingFields = []) {
        // IMPROVEMENT: This code snippet is repeated multiple times.
        // Maybe it's better to create a function for it.
        const currentPartner = this.currentOrder.get_partner();
        console.log("This is the currently Order: ", this.currentOrder)
        const partnerScreenProps = { partner: currentPartner };
        if (isEditMode && currentPartner) {
            partnerScreenProps.editModeProps = true;
            partnerScreenProps.missingFields = missingFields;
        }
        const { confirmed, payload: newPartner } = await this.pos.showTempScreen(
            "PartnerListScreen",
            partnerScreenProps
        );
        if (confirmed) {
            this.currentOrder.set_partner(newPartner);
            this.updateDeliveryMethodsInfo()
        }
    },

    deliveryButtonAbility(deliveryMethodId, deliveryMethodName) {
        const price = this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].price

        if (price)
            return false;
        return true;
    },

    deliveryButtonClass(deliveryMethodId, deliveryMethodName) {
        const clicked = this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].clicked

        if (clicked)
            return true;
        return false;
    },

    getDeliveryMethodsSetupInfo() {
        const delivery_methods = this.delivery_methods;
        let delivery_methods_info = {}
        delivery_methods.forEach((delivery_method) => {
            delivery_methods_info[delivery_method.name + '_' + delivery_method.id] = {
                'name': delivery_method.name,
                'price': null,
                'currency': "",
                'displayed_name': delivery_method.name,
                'clicked': false,
                'order_line': null
            }
        });
        return delivery_methods_info;
    },

    async deliveryMethodInfo(deliveryMethodId, deliveryMethodName) {
        const currentOrder = this.currentOrder;
        console.log("This is the current Order: ", currentOrder)
        const currentPartner = this.currentOrder.get_partner();
        let price = null;
        let name = null

        if (currentPartner) {
            const order = {
                partner_shipping_id: currentPartner,
                pricelist_id: currentOrder.pricelist ? currentOrder.pricelist : null,
                website_id: currentOrder.pos.config
            }
            try {
                const result = await jsonrpc('/pos/mealshift-delivery-provider/request-quote', {
                    delivery_method_id: deliveryMethodId,
                    order: order
                });
                price = result.price
                if (price) {
                    name = deliveryMethodName + ": " + price + "$";
                } else {
                    name = result.error_message;
                }
            } catch (error) {
                console.log("This is the error: ", error);
                name = "Unknown Error!"
            }
        } else {
            price = null;
            name = deliveryMethodName;
        }

        this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].price = price
        this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].displayed_name = name
    },

    updateDeliveryMethodsInfo() {
        const delivery_methods = this.delivery_methods;
        delivery_methods.forEach((delivery_method) => {
            this.deliveryMethodInfo(delivery_method.id, delivery_method.name)
        })
    },

    checkDeliveryMethodProduct(deliveryMethodId) {
        const delivery_methods = this.delivery_methods;
        let product = null;
        delivery_methods.forEach((delivery_method) => {
            if (delivery_method.id === deliveryMethodId) {

                if (delivery_method.product_barcode) {
                    let delivery_product = this.pos.db.get_product_by_id(delivery_method.product_id[0]);
                    if (!delivery_product)
                        delivery_product = this.pos.db.get_product_by_id(delivery_method.product_barcode);
                    product = delivery_product
                }
            }
        })
        return product;
    },

    checkDeliveryOrderLine() {
        const order_lines = this.currentOrder.orderlines;
        order_lines.forEach((order_line) => {
            if (order_line.delivery_method) {
                this.state.delivery_methods_info[order_line.delivery_method].clicked = true;
                this.state.delivery_methods_info[order_line.delivery_method].order_line = order_line;
            }
        })
    },

    checkDeliveryMethodButtonsState(deliveryMethodKey) {
        for (const key in this.state.delivery_methods_info) {
            if (key !== deliveryMethodKey) {
                if (this.state.delivery_methods_info[key].clicked) {
                    this.state.delivery_methods_info[key].clicked = false
                    const order_line = this.state.delivery_methods_info[key].order_line;
                    this.currentOrder.orderlines.remove(order_line)
                }
            }
        }
    },

    async addDeliveryMethod(deliveryMethodId, deliveryMethodName) {
        const product = this.checkDeliveryMethodProduct(deliveryMethodId);
        if (!product) {
            return this.popup.add(ErrorPopup, {
                title: _t("Error: Delivery Product"),
                body: _t("The product linked with this delivery method should be applied within the POS!"),
            });
        }

        const deliveryMethodClicked = this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].clicked
        if (!deliveryMethodClicked) {
            this.checkDeliveryMethodButtonsState(deliveryMethodName + '_' + deliveryMethodId)
            const deliveryMethodPrice = this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].price

            const new_line = this.currentOrder.orderlines[0].clone()
            new_line.product = product
            new_line.set_product_lot(product)
            new_line.price = deliveryMethodPrice;
            new_line.delivery_method = deliveryMethodName + '_' + deliveryMethodId;

            this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].order_line = new_line
            this.currentOrder.add_orderline(new_line);

            this.currentOrder.carrier_id = deliveryMethodId;
        } else {
            const order_line = this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].order_line;
            this.currentOrder.orderlines.remove(order_line)

            this.currentOrder.carrier_id = null;
        }

        this.state.delivery_methods_info[deliveryMethodName + '_' + deliveryMethodId].clicked = !deliveryMethodClicked
    }


})