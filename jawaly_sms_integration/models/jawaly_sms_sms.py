import logging

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class JawalySmsSms(models.Model):
    _inherit = "sms.sms"

    # def send(self, unlink_failed=False, unlink_sent=True, auto_commit=False, raise_exception=False):
    #     print("Yes printed from inherited class")
    #     res = super(JawalySmsSms, self).send(unlink_failed=False, unlink_sent=True, auto_commit=False, raise_exception=False)
    #     return res

    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        print("Yes private function override it in inherited class")
        """ This method tries to send SMS after checking the number (presence and
        formatting). """
        print("real send function fired")
        iap_data = [{
            'res_id': record.id,
            'number': record.number,
            'content': record.body,
        } for record in self]
        print("this is iap_data", iap_data)

        try:
            print("we enter try in send real")
            _logger.info("this is iap data")
            _logger.info(iap_data)
            iap_results = self.env['sms.api']._send_sms_batch(iap_data)
        except Exception as e:
            _logger.info('Sent batch %s SMS: %s: failed with exception %s', len(self.ids), self.ids, e)
            if raise_exception:
                raise
            self._postprocess_iap_sent_sms(
                [{'res_id': sms.id, 'state': 'server_error'} for sms in self],
                unlink_failed=unlink_failed, unlink_sent=unlink_sent)
        else:
            _logger.info('Send batch %s SMS: %s: gave %s', len(self.ids), self.ids, iap_results)
            self._postprocess_iap_sent_sms(iap_results, unlink_failed=unlink_failed, unlink_sent=unlink_sent)
        print("Yes all working fine")
