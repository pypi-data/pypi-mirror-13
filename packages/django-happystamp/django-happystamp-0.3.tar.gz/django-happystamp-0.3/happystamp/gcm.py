import requests
import json

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import django.dispatch

post_push=django.dispatch.Signal(providing_args=["message", "reg_id", "error", "kwargs"])

class BaseGCMMessage(object):

    def __init__(self):
        self.api_key = settings.GCM_API_KEY

        if not self.api_key:
            raise ImproperlyConfigured(
                "You haven't set the 'GCM_API_KEY' setting yet.")

    def _chunks(self, items, limit):      
        for i in range(0, len(items), limit):
            yield items[i:i + limit]

    def send(self, regs_id, data, **kwargs):
        """
        Send a GCM message for one or more devices, using json data
        regs_id: A list with the devices which will be receiving a message
        data: The dict data which will be send
        Optional params e.g.:
            collapse_key: A string to group messages
        For more info see the following documentation:
        https://developer.android.com/google/gcm/server-ref.html#send-downstream
        """
        if len(regs_id) > settings.GCM_MAX_RECIPIENTS:
            ret = []
            for chunk in self._chunks(regs_id, settings.GCM_MAX_RECIPIENTS):
                ret.append(self.send(chunk, data, **kwargs))
            return ret

        values = {
            'registration_ids': regs_id,
            'data': data,
            'collapse_key': 'message'}
        values.update(kwargs)

        values = json.dumps(values)

        headers = {
            'UserAgent': "GCM-Server",
            'Content-Type': 'application/json',
            'Authorization': 'key=' + self.api_key}

        response = requests.post(url="https://android.googleapis.com/gcm/send",
                                 data=values,
                                 headers=headers)
        response.raise_for_status()
        json_content = response.content.decode("utf-8")
        return data, regs_id, json.loads(json_content)

class GCMMessage(BaseGCMMessage):
    GCM_INVALID_ID_ERRORS = ['InvalidRegistration',
                             'NotRegistered',
                             'MismatchSenderId']

    def send(self, regs_id, data, **kwargs):
        response = super(GCMMessage, self).send(regs_id, {'msg': data})
        chunks = [response] if not isinstance(response, list) else response
        for chunk in chunks:
            self.post_send(*chunk, **kwargs)
            
        return response

    def post_send(self, data, regs_id, response, **kwargs):
        invalid_messages = {}
            
        if response['failure']:
            invalid_messages = dict(filter(
                lambda x: x[1].get('error') in self.GCM_INVALID_ID_ERRORS,
                zip(regs_id, response.get('results'))))
                    
        for reg_id in regs_id:
            if reg_id in invalid_messages:
                post_push.send(sender=self.__class__, 
                               message=data,
                               reg_id=reg_id, 
                               error=invalid_messages[reg_id]['error'],
                               **kwargs
                               )
            else:
                post_push.send(sender=self.__class__, 
                               message=data,
                               reg_id=reg_id, 
                               error=None,
                               **kwargs
                               )
