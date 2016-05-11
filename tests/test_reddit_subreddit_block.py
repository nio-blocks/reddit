from collections import defaultdict
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from ..reddit_subreddit_block import SubredditFeed
from ..http_blocks.rest.rest_block import RESTPolling
from unittest.mock import patch, MagicMock


class TestSubredditFeed(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        # This will keep a list of signals notified for each output
        self.last_notified = defaultdict(list)

    @patch("requests.post")
    def test_authenticate(self, mock_post):
        """ Test that headers are properly set in _authenticate. """
        blk = SubredditFeed()
        mock_post.return_value = MagicMock()
        blk.get_token = MagicMock(return_value="TEST TOKEN")
        headers = blk._authenticate()
        self.assertEqual(headers, {'User-Agent': 'nio', 'Authorization': 'bearer TEST TOKEN'})

    @patch("requests.post")
    @patch("requests.get")
    def test_prepare_url(self, mock_post, mock_get):
        """ Test that our url has a before query parameter and appends the proper subreddit. """
        blk = SubredditFeed()
        mock_post.return_value = MagicMock()
        mock_get.return_value = MagicMock()
        blk.post_ids = ["RedditID"]
        self.configure_block(blk, {
            "queries": ["baz"]
        })
        blk.poll()
        self.assertEqual(blk.url, "https://oauth.reddit.com/r/baz/new.json?before=RedditID")

    @patch.object(SubredditFeed, "_authenticate")
    @patch("requests.get")
    def test_process_response(self, mock_get, mock_auth):
        """ Test that our _process_response method returns a single signal object. """
        blk = SubredditFeed()
        blk.get_token = MagicMock()
        self.configure_block(blk, {
            "queries": [
                "foo",
                "bar"
            ]
        })
        mock_get.return_value = MagicMock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = \
            {'data':
                {'children': [
                    {'data':
                        {
                            'name': 'uniqueRedditID',
                            "subreddit": "IOT",
                            "author": "the author"
                        }
                    }
                ]}
            }
        blk.poll()

        self.assert_num_signals_notified(1)
        last_sig = self.last_notified['default'][0]
        self.assertEqual(last_sig.name, "uniqueRedditID")
        self.assertEqual(last_sig.subreddit, "IOT")
        self.assertEqual(last_sig.author, "the author")
