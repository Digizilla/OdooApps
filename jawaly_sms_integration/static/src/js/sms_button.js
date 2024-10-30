/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import core from 'web.core';
import utils from 'web.utils';


registerPatch({
    name: 'Chatter',
    recordMethods: {
        async onClickSendSMS(event) {
            const hash = window.location.hash;
            const params = new URLSearchParams(hash.substring(hash.indexOf('?') + 1));
            var activeId = params.get('id');
            const model = params.get('model');

//            console.log(model, params )
//             if (model === 'sale.order') {
//                const saleOrder = await this.env.services['orm'].read('sale.order', [parseInt(activeId)], ['partner_id']);
//                if (saleOrder.length) {
//                    activeId = saleOrder[0].partner_id[0];
//                }
//            }

            const action = await this.env.services['action'].doAction({
                type: 'ir.actions.act_window',
                res_model: 'sms.composer',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    'default_composition_mode': 'comment',
                    'default_res_id': activeId,
                    'default_res_model': model,
                }
            });
            console.log('res_id', activeId)
        },
    },
});