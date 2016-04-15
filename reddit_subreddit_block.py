from .http_blocks.rest.rest_block import RESTPolling
from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import VersionProperty


@Discoverable(DiscoverableType.block)
class SubredditFeed(RESTPolling):

    """ This block polls the Reddit feed for subreddits that match the queries.

    Attributes:
        queries (List(str)): Reddit subreddits to query.

    """

    version = VersionProperty('0.1.0')

    URL_FORMAT = ("https://www.reddit.com/r/{}.json")

    # TODO: initialize queries attribute
    # queries = ["nba"]

    def __init__(self):
        super().__init__()

    def configure(self, context):
        super().configure(context)

    def start(self):
        super().start()

    def _prepare_url(self):
        self.url = self.URL_FORMAT.format(self.current_query)

    def process_signals(self, signals, input_id='default'):
        for signal in signals:
            pass
        self.notify_signals(signals, output_id='default')
