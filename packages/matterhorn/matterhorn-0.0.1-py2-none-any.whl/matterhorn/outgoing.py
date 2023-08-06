

# receiving messages from mattermost

from flask import request

class Downhill(object):
    def __init__(self, blueprint, token=None, username=None, icon_url=None):
        # config is overriten by matterhorn later
        self.matterhorn_config = {}


        self.blueprint = blueprint
        self.token = token

        self.username = username
        self.icon_url = icon_url

        self.map = {}

        blueprint.route('/')(self._receive)

    def _receive():
        data = request.form

        if data.get('token', None) != TOKEN:
            print 'Invalid TOKEN'
            return 'Invalid Token', 400


    def __call__(self, pattern, **options):
        pattern = pattern.strip().split()[0]

        def inner(func):
            self.map[pattern] = func
            return func

        return inner