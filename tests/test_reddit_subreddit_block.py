from collections import defaultdict
from nio.util.support.block_test_case import NIOBlockTestCase
from ..reddit_subreddit_block import SubredditFeed
from unittest.mock import patch, MagicMock


class TestSubredditFeed(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        # This will keep a list of signals notified for each output
        self.last_notified = defaultdict(list)

    def test_authenticate(self):
        """ Test that headers are properly set after _authenticate. """
        blk = SubredditFeed()
        blk.get_token = MagicMock(return_value="TEST TOKEN")
        blk._authenticate()
        headers = blk._get_headers()
        self.assertEqual(headers,
                         {'User-Agent': 'nio',
                          'Authorization': 'bearer TEST TOKEN'})

    def test_prepare_url(self):
        """ Test url has a before query param and appends proper subreddit. """
        blk = SubredditFeed()
        blk.init_post_id = MagicMock()
        blk.get_token = MagicMock(return_value="TEST TOKEN")
        blk.post_ids = ["RedditID"]
        self.configure_block(blk, {
            "queries": ["baz"]
        })
        blk._prepare_url(False)
        self.assertEqual(
            blk.url, "https://oauth.reddit.com/r/baz/new.json?before=RedditID")

    def test_process_response(self):
        """ Test that _process_response returns a single signal object. """
        blk = SubredditFeed()
        blk.init_post_id = MagicMock()
        blk.get_token = MagicMock(return_value="TEST TOKEN")
        blk.post_ids = ["RedditID"]
        self.configure_block(blk, {
            "queries": [
                "foo"
            ]
        })
        expected_response = {
            'data': {
                'children': [{
                    'data': {
                        "name": 'uniqueRedditID',
                        "subreddit": "IOT",
                        "author": "the author"
                    }
                }]
            }
        }
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock()
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = expected_response
            blk.poll()

        self.assert_num_signals_notified(1)
        last_sig = self.last_notified['default'][0]
        self.assertEqual(last_sig.name, "uniqueRedditID")
        self.assertEqual(last_sig.subreddit, "IOT")
        self.assertEqual(last_sig.author, "the author")
