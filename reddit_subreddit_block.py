from .http_blocks.rest.rest_block import RESTPolling
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import VersionProperty
from nio.metadata.properties import PropertyHolder, StringProperty, \
    ObjectProperty, BoolProperty
from nio.common.signal.base import Signal

import requests

class Creds(PropertyHolder):
    """ PropertyHolder for Reddit credentials.
    """
    client_id = StringProperty(title='Client ID', default='[[REDDIT_CLIENT_ID]]')
    app_secret = StringProperty(title='App Secret', default='[[REDDIT_SECRET]]')
    app_username = StringProperty(title='App Username', default='[[REDDIT_USERNAME]]')
    app_password = StringProperty(title='App Password', default='[[REDDIT_PASSWORD]]')

class SubredditSignal(Signal):
    def __init__(self, data):
        super().__init__()
        for k in data:
            setattr(self, k, data[k])

@Discoverable(DiscoverableType.block)
class SubredditFeed(RESTPolling):

    """ This block polls the Reddit feed for subreddits that match the queries.

    Properties:
        queries (List(str)): Reddit subreddits to query.
        creds (APICredentials): API credentials
    """

    version = VersionProperty('0.1.0')

    URL_FORMAT = ("https://oauth.reddit.com/r/{}/new.json?before={}")

    creds = ObjectProperty(Creds, title='Credentials')

    # TODO: initialize queries attribute
    # queries = ["nba", "iot"]

    def __init__(self):
        super().__init__()
        self.paging_marker_post_id = ""

    def configure(self, context):
        super().configure(context)

    def start(self):
        super().start()

    def get_token(self):
        # self._logger.debug(self.creds.client_id)
        client_auth = requests.auth.HTTPBasicAuth(self.creds.client_id, self.creds.app_secret)
        post_data = {"grant_type": "password", "username": self.creds.app_username, "password": self.creds.app_password}
        headers = {"User-Agent": "nio"}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        return response.json()['access_token']

    def _get_post_id(self, post):
        """ Returns a uniquely identifying string (name) for a post.

        Args:
            post (dict): A post.
        Returns:
            name (string): A string that uniquely identifies a
                         post. None indicated that the post should
                         be treated as unique.
        """
        return post['data']['name']

    def _prepare_url(self, paging):
        """ Overridden from RESTPolling block.

        Appends the Client ID to the response string and builds the headers dictionary.

        Args:
            paging (bool): Are we paging?

        Returns:
            headers
        """
        token = self.get_token();
        headers = {"Authorization": "bearer " + token, "User-Agent": "nio"}
        response = requests.get(self.URL_FORMAT.format(self.current_query, self.paging_marker_post_id), headers=headers)
        self.url = response.url
        self._logger.debug("********")
        self._logger.debug(response.request.headers)
        # self._logger.debug("POST ID " + self.paging_marker_post_id)

        # if not paging:
            # self.paging_url = None
            # header['count'] = 25
            # header['before'] = self.paging_marker_post_id

        # else:
            # self._logger.debug("PAGING")
            # q_params = {"count": "25", "before": paging_marker_post_id}
            # headers.update(q_params)
            # self._logger.debug(headers)
            # response = requests.get(self.URL_FORMAT.format(self.current_query), headers=headers)
            # self.paging_url = response.url

        return headers

    def _process_response(self, resp):
        """ Extract posts from the Subreddit API response object.

        Args:
            resp (Response)

        Returns:
            signals (list(Signal)): List of signals to notify, each of which
                corresponds to a new Subreddit post.
            paging (bool): Denotes whether or not paging requests are necessary.
        """
        signals = []
        paging = False
        resp = resp.json()
        posts = resp['data']['children']

        # self._logger.debug(self.page_num)
        # if self.page_num > 1:
        #     paging = True
        self._logger.debug("Reddit response contains %d posts" % len(posts))
        self._logger.debug(paging)

        if posts:
            self._logger.debug("$$$ Setting new post id $$$")
            self._logger.debug("Old Post id: " + self.paging_marker_post_id)
            self.paging_marker_post_id = self._get_post_id(posts[0])
            self._logger.debug("Newest Post id: " + self.paging_marker_post_id)
        for post in posts:
            signals.append(SubredditSignal(post))
        if len(posts) == 25:
            paging = True

        return signals, paging


    # def process_signals(self, signals, input_id='default'):
    #     self._logger.debug("processing signals")
    #     for signal in signals:
    #         pass
    #     self.notify_signals(signals, output_id='default')
