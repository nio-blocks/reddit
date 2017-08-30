from unittest.mock import patch, MagicMock

from nio.testing.block_test_case import NIOBlockTestCase
from nio.block.terminals import DEFAULT_TERMINAL

from ..reddit_subreddit_block import SubredditFeed


class TestSubredditFeed(NIOBlockTestCase):

    def test_authenticate(self):
        """ Test that headers are properly set after _authenticate. """
        blk = SubredditFeed()
        blk.get_token = MagicMock(return_value="TEST TOKEN")
        blk._authenticate()
        headers = blk._get_headers()
        self.assertEqual(headers,
                         {'User-Agent': 'nio',
                          'Authorization': 'bearer TEST TOKEN'})

    def test_authenticate_error(self):
        """ Test that headers are properly set after _authenticate. """
        blk = SubredditFeed()
        # Simulate a failure to parse JSON in the token retrieval
        blk.get_token = MagicMock(side_effect=ValueError)
        blk._authenticate()
        self.assertIsNone(blk.token)

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
        last_sig = self.last_notified[DEFAULT_TERMINAL][0]
        self.assertEqual(last_sig.name, "uniqueRedditID")
        self.assertEqual(last_sig.subreddit, "IOT")
        self.assertEqual(last_sig.author, "the author")

    def test_process_response_exception(self):
        """ Test that _process_response can handle exceptions """
        blk = SubredditFeed()
        blk.init_post_id = MagicMock()
        blk._epilogue = MagicMock()
        blk.get_token = MagicMock(return_value="TEST TOKEN")
        blk.post_ids = ["RedditID"]
        self.configure_block(blk, {
            "queries": [
                "foo"
            ]
        })
        mock_resp = MagicMock()
        # We want to simulate an exception when trying to parse json
        mock_resp.json = MagicMock(side_effect=AttributeError)
        mock_resp.status_code = 200
        with patch("requests.get") as mock_get:
            mock_get.return_value = mock_resp
            blk.poll()

        # We should not have notified any signals with the exception
        self.assert_num_signals_notified(0)
        # But the epilogue should have still been called to generate the poll
        blk._epilogue.assert_called_once_with()
