

'''
Incoming Webhooks
~~~~~~~~~~~~~~~~~

Provides API for `uphill` messages.

'''

import requests

class Uphill(object):
    def __init__(self, url, channel=None, username=None, icon_url=None):
        # mattermost server url
        self.url = url

        # channel to send to 
        self.channel = channel
        self.username = username
        self.icon_url = icon_url

    def _update_payload(payload, options):
        for option in 'channel', 'username', 'icon_url':
            if option in options:
                payload[option] = options[option]
            else:
                value = gettattr(self, option, None)
                if value is not None:
                    payload[option] = value

        return payload

    def send(self, message, **options):
        payload = self._update_payload({
            'text': message 
        }, options)

        req = requests.post(
            self.url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload),
            verify=False)

        if r.status_code is not requests.codes.ok:
            print 'Error'


