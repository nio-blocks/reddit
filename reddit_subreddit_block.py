from .http_blocks.rest.rest_block import RESTPolling
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import VersionProperty
from nio.metadata.properties import PropertyHolder, StringProperty, \
    ObjectProperty, BoolProperty
from nio.common.signal.base import Signal

import requests

class Creds(PropertyHolder):
    """
    """
    client_id = StringProperty(title='Client ID', default='[[REDDIT_CLIENT_ID]]')
    app_secret = StringProperty(title='App Secret', default='[[REDDIT_SECRET]]')
    app_username = StringProperty(title='App Username', default='[[REDDIT_USERNAME]]')
    app_password = StringProperty(title='App Password', default='[[REDDIT_PASSWORD]]')

@Discoverable(DiscoverableType.block)
class SubredditFeed(RESTPolling):

    """ This block polls the Reddit feed for subreddits that match the queries.

    Attributes:
        queries (List(str)): Reddit subreddits to query.

    """

    version = VersionProperty('0.1.0')

    URL_FORMAT = ("https://oauth.reddit.com/r/{}.json?{}")

    creds = ObjectProperty(Creds, title='Credentials')

    # TODO: initialize queries attribute
    # queries = ["nba"]

    def __init__(self):
        super().__init__()

    def configure(self, context):
        super().configure(context)

    def start(self):
        super().start()

    def get_token(self):
        self._logger.debug(self.creds.client_id)
        client_auth = requests.auth.HTTPBasicAuth(self.creds.client_id, self.creds.app_secret)
        post_data = {"grant_type": "password", "username": self.creds.app_username, "password": self.creds.app_password}
        headers = {"User-Agent": "nio"}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        self._logger.debug(response.json())
        self._logger.debug(response.json()['access_token'])
        return response.json()['access_token']

    def _prepare_url(self, paging):
        token = self.get_token();
        self._logger.debug("TOKEN: " + token)
        headers = {"Authorization": "bearer " + token, "User-Agent": "nio"}
        # TODO: clean up this function
        response = requests.get("https://oauth.reddit.com/r/iot.json", headers=headers)
        self._logger.debug(response.json())
        self.url = self.URL_FORMAT.format(self.current_query, "Authorization=bearer%20{}&User-Agent=nio".format(token))


    def process_signals(self, signals, input_id='default'):
        self._logger.debug("processing signals")
        for signal in signals:
            pass
        self.notify_signals(signals, output_id='default')
