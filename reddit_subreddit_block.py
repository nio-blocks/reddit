import requests

from nio.properties import PropertyHolder, StringProperty, \
    ObjectProperty, VersionProperty
from nio.signal.base import Signal

from .rest_polling.rest_block import RESTPolling


class Creds(PropertyHolder):
    """ PropertyHolder for Reddit credentials. """
    client_id = StringProperty(title='Client ID',
                               default='[[REDDIT_CLIENT_ID]]')
    app_secret = StringProperty(title='App Secret',
                                default='[[REDDIT_SECRET]]')
    app_username = StringProperty(title='App Username',
                                  default='[[REDDIT_USERNAME]]')


class SubredditSignal(Signal):
    pass


class SubredditFeed(RESTPolling):
    """
    This block polls Reddit feed.

    Notifies the most recent posts in subreddits that match the queries.

    Properties: creds (APICredentials): API credentials
    """

    version = VersionProperty("0.1.2")

    URL_FORMAT = ("https://oauth.reddit.com/r/{}/new.json?before={}")

    # the default number of posts returned by the Reddit API
    DEFAULT_LIMIT = 25

    creds = ObjectProperty(Creds, title='Credentials')

    def __init__(self):
        super().__init__()
        self.post_ids = []
        self.token = None

    def configure(self, context):
        """
        Configures block.

        Sets up a new instance for each query, and captures the id of the most
        recent post.
        """
        super().configure(context)
        for query in self.queries():
            self.init_post_id(query)

    def start(self):
        super().start()

    def _authenticate(self):
        """
        Overridden from RESTPolling block.

        Retrieves the OAuth token and saves it to the instance. If there is
        an error during authentication, the token will be set to None.
        """
        try:
            self.token = self.get_token()
        except:
            self.logger.exception("Error authenticating, invalidating token")
            self.token = None

    def init_post_id(self, query):
        """
        Makes an initial request to the API.

        Determines the id of the most recent post, which becomes the 'before'
        query parameter, i.e., the marker from where to start polling.

        Args: query (string): The name of the subreddit.
        """
        headers = self._get_headers()
        response = requests.get(self.URL_FORMAT.format(query, None),
                                headers=headers)
        resp = response.json()
        self.post_ids.append(resp['data']['children'][0]['data']['name'])

    def get_token(self):
        """
        Gets token required for header in each request.

        Returns: access_token (string): Identifier that allows OAuth API access
        """

        self.logger.debug("Obtaining access token")
        client_auth = requests.auth.HTTPBasicAuth(self.creds().client_id(),
                                                  self.creds().app_secret())
        post_data = "grant_type=client_credentials"
        headers = {"User-Agent": "nio"}
        response = requests.post("https://www.reddit.com/api/v1/access_token",
                                 auth=client_auth,
                                 data=post_data,
                                 headers=headers)

        return response.json()['access_token']

    def _get_post_id(self, signal):
        """
        Overridden from RESTPolling block.

        Returns a uniquely identifying string (name) for a signal.

        Args: signal (Signal): A post formatted as a Signal.
        Returns: name (string): A string that uniquely identifies a signal.
        """

        return signal.name

    def _get_headers(self):
        """ Get the headers for a request using our current token.

        If the token does not exist, this method will call authenticate
        to attempt to retrieve a valid token.

        Returns:
            headers (dict): A dictionary containing the HTTP headers for
                a valid request
        """
        if not self.token:
            self._authenticate()

        return {
            "Authorization": "bearer " + self.token,
            "User-Agent": "nio"
        }

    def _prepare_url(self, paging):
        """
        Overridden from RESTPolling block.

        Appends the current query and the post_id (before query parameter)
        to the URL.

        Args: paging (bool): Are we paging?

        Returns:
        headers (dict): the headers sent to poll method in RESTPolling.
        """
        self.url = self.URL_FORMAT.format(self.current_query,
                                          self.post_ids[self._idx])
        return self._get_headers()

    def _process_response(self, resp):
        """
        Overridden from RESTPolling block.

        Extract posts from the Subreddit API response object.

        Args: resp (Response): response object containing most recent posts.

        Returns:
        signals (list(Signal)): List of signals to notify, each of which
        corresponds to a new Subreddit post since the last poll.
        paging (bool): Denotes whether paging requests are needed.
        """

        signals = []
        paging = False
        try:
            resp = resp.json()
            posts = resp['data']['children']
        except:
            # We don't expect this to get hit too often, because we know that
            # we have a 200 response by the time we get here. But we've seen
            # the Reddit API return some non-JSON even with a 200 at times
            self.logger.exception("Error processsing response: {}".format(
                resp.text))
            posts = []

        self.logger.debug("Reddit response contains %d posts" % len(posts))

        for post in posts:
            signals.append(SubredditSignal(post['data']))

        if signals:
            self.post_ids[self._idx] = self._get_post_id(signals[0])

        if len(posts) == self.DEFAULT_LIMIT:
            paging = True

        return signals, paging
