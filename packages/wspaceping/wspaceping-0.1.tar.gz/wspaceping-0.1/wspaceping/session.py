import requests

from wspaceping.constants import html_headers


class SiggySession:
    def __init__(self, session_id, user_id, pass_hash):
        self.session_id = session_id
        self.user_id = user_id
        self.pass_hash = pass_hash

        self.cookiejar = {
            'sessionID': self.session_id,
            'userID': self.user_id,
            'passHash': self.pass_hash
        }

    @classmethod
    def from_login(cls, username, password):
        data = requests.get('https://siggy.borkedlabs.com/pages/welcome')

        session_id = data.cookies['sessionID']

        payload = {
            'bounce': '',
            'username': username,
            'password': password
        }

        data = requests.post(
            'https://siggy.borkedlabs.com/account/login',
            data=payload,
            headers=html_headers,
            allow_redirects=False
        )

        return cls(
            session_id,
            data.cookies['userID'],
            data.cookies['passHash']
        )
