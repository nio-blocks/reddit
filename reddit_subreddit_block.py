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

    def __init__(self):
        super().__init__()
        self.post_ids = []

    def configure(self, context):
        super().configure(context)
        self._logger.debug(self.queries)
        for query in self.queries:
            self._logger.debug("QUERY: " + query)
            self.init_post_id(query);

    def init_post_id(self, query):
        self._logger.debug("inside init_post_id")
        token = self.get_token();
        headers = {"Authorization": "bearer " + token, "User-Agent": "nio"}
        self._logger.debug(self._idx)
        self._logger.debug(self.post_ids)
        # TODO: set first post_id to none (we don't have a before query param)
        response = requests.get(self.URL_FORMAT.format(query, None), headers=headers)
        resp = response.json()
        self._logger.debug("made it through get request")
        self._logger.debug(resp['data']['children'][0]['data']['name'])
        self.post_ids.append(resp['data']['children'][0]['data']['name'])

    def start(self):
        super().start()

    def get_token(self):
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
        response = requests.get(self.URL_FORMAT.format(self.current_query, self.post_ids[self._idx]), headers=headers)
        self.url = response.url
        self._logger.debug("********")

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

        self._logger.debug("Reddit response contains %d posts" % len(posts))

        if posts:
            # self._logger.debug("$$$ Setting new post id $$$")
            # self._logger.debug("Old Post id: " + self.post_ids[self._idx])
            self._logger.debug("###")
            self._logger.debug(self.post_ids)
            self._logger.debug(self._idx)
            self.post_ids[self._idx] = self._get_post_id(posts[0])
            self._logger.debug(self.post_ids[self._idx])
            # self._logger.debug("Newest Post id: " + self.post_ids[self._idx])
        for post in posts:
            self._logger.debug(SubredditSignal(post))
            self._logger.debug(signals)
            signals.append(SubredditSignal(post))
        if len(posts) == 25:
            self._logger.debug("Paging set to true")
            paging = True

        return signals, paging
