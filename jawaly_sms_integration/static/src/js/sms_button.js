/** @odoo-module **/
import { registerPatch } from '@mail/model/model_core';
import core from 'web.core';
import utils from 'web.utils';


registerPatch({
    name: 'Chatter',
    recordMethods: {
        async onClickSendSMS(event) {
             if (this && this.isTemporary) {
                const saved = await this.doSaveRecord();
                if (!saved) {
                    return;
                }
                else {
                    this.sendSMS();
                    return;
                }
            }
            this.sendSMS();
        },
        async sendSMS() {
            const hash = window.location.hash;
            const params = new URLSearchParams(hash.substring(hash.indexOf('?') + 1));
            let activeId = params.get('id') || params.get('#id');
            const model = params.get('model');


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
    }


});