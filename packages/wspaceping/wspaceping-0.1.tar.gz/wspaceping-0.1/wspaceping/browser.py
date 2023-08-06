import requests
import json
import time

from wspaceping.session import SiggySession
from wspaceping.constants import json_headers


class SiggyBrowser:
    def __init__(self, username, password):
        self.session = SiggySession.from_login(username, password)

    def refresh(self):
        states = {
            'statsOpen': False,
            'sigsAddOpen': True,
            'posesOpen': True,
            'dscanOpen': True,
            'map': {
                'open': True,
                'height': 633,
            },
            'sigFilters': {
                'wh': True,
                'ore': True,
                'gas': True,
                'data': True,
                'relic': True,
                'anomaly': True,
                'none': True
            }
        }

        cookies = {
            'display_states': json.dumps(states),
            'notesUpdate': str(time.time() - 5)
        }

        cookies.update(self.session.cookiejar)

        payload = {
            'systemID': '31002238',
            'lastUpdate': str(time.time() - 5),
            'mapOpen': 'true',
            'mapLastUpdate': str(time.time() - 5),
            'forceUpdate': 'true'
        }

        result = requests.post(
            'https://siggy.borkedlabs.com/siggy/siggy',
            cookies=cookies,
            headers=json_headers,
            data=payload
        ).json()

        return result
