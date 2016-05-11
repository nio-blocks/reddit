from .http_blocks.rest.rest_block import RESTPolling
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import VersionProperty
from nio.metadata.properties import PropertyHolder, StringProperty, \
    ObjectProperty, BoolProperty
from nio.common.signal.base import Signal

import requests

class Creds(PropertyHolder):
    """ PropertyHolder for Reddit credentials. """
    client_id = StringProperty(title='Client ID', default='[[REDDIT_CLIENT_ID]]')
    app_secret = StringProperty(title='App Secret', default='[[REDDIT_SECRET]]')
    app_username = StringProperty(title='App Username', default='[[REDDIT_USERNAME]]')
    app_password = StringProperty(title='App Password', default='[[REDDIT_PASSWORD]]')

class SubredditSignal(Signal):
    """ Translates attributes from subreddit posts into Signal format """
    def __init__(self, data):
        super().__init__()
        for k in data:
            setattr(self, k, data[k])

@Discoverable(DiscoverableType.block)
class SubredditFeed(RESTPolling):

    """ This block polls the Reddit feed for the most recent posts in subreddits that match the queries.

        Properties:
            creds (APICredentials): API credentials
    """

    version = VersionProperty('0.1.0')

    URL_FORMAT = ("https://oauth.reddit.com/r/{}/new.json?before={}")

    # the default number of posts returned by the Reddit API
    DEFAULT_LIMIT = 25

    creds = ObjectProperty(Creds, title='Credentials')

    def __init__(self):
        super().__init__()
        self.post_ids = []

    def configure(self, context):
        """ Configures block, sets up a new instance for each query, and
            captures the id of the most recent post.
        """
        super().configure(context)
        for query in self.queries:
            self.init_post_id(query);

    def start(self):
        super().start()

    def _authenticate(self):
        """ Overridden from RESTPolling block.

            Sets up headers with OAuth token.
        """
        self.token = self.get_token();
        headers = {"Authorization": "bearer " + self.token, "User-Agent": "nio"}

        return headers

    def init_post_id(self, query):
        """ Makes the initial request to determine the id of the most recent
            post, which becomes the 'before' query parameter, i.e., the marker
            from where to start polling.

            Args:
                query (string): The name of the subreddit.

        """
        headers = self._authenticate()
        response = requests.get(self.URL_FORMAT.format(query, None), headers=headers)
        resp = response.json()
        self.post_ids.append(resp['data']['children'][0]['data']['name'])

    def get_token(self):
        """ Gets token required for header in each request.

            Returns:
                access_token (string): An identifier that allows OAuth API access
        """

        client_auth = requests.auth.HTTPBasicAuth(self.creds.client_id, self.creds.app_secret)
        post_data = {"grant_type": "password", "username": self.creds.app_username, "password": self.creds.app_password}
        headers = {"User-Agent": "nio"}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)

        return response.json()['access_token']

    def _get_post_id(self, signal):
        """ Overridden from RESTPolling block.

            Returns a uniquely identifying string (name) for a signal.

            Args:
                signal (dict): A signal.
            Returns:
                name (string): A string that uniquely identifies a
                             signal.
        """

        return signal.name

    def _prepare_url(self, paging):
        """ Overridden from RESTPolling block.

            Calls _authenticate to build the headers, and appends the current
            query and the post_id (before query parameter) to the URL.

            Args:
                paging (bool): Are we paging?

            Returns:
                headers (dict):  the headers that will be sent to the poll method in RESTPolling.
        """

        headers = self._authenticate()
        self.url = self.URL_FORMAT.format(self.current_query, self.post_ids[self._idx])

        return headers

    def _process_response(self, resp):
        """ Overridden from RESTPolling block.

            Extract posts from the Subreddit API response object.

            Args:
                resp (Response): the response object containing the most recent posts.

            Returns:
                signals (list(Signal)): List of signals to notify, each of which
                    corresponds to a new Subreddit post since the last poll.
                paging (bool): Denotes whether or not paging requests are necessary.
        """

        signals = []
        paging = False
        resp = resp.json()
        posts = resp['data']['children']

        self._logger.debug("Reddit response contains %d posts" % len(posts))

        for post in posts:
            signals.append(SubredditSignal(post['data']))

        if signals:
            self.post_ids[self._idx] = self._get_post_id(signals[0])

        if len(posts) == self.DEFAULT_LIMIT:
            paging = True

        return signals, paging
