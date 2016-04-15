from collections import defaultdict
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase
from ..reddit_subreddit_block import SubredditFeed


class TestSubredditFeed(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        # This will keep a list of signals notified for each output
        self.last_notified = defaultdict(list)

    def test_prepare_url(self):
        blk = SubredditFeed()
        self.configure_block(blk, {
            "queries": ["foobar"]
        })

        def prepare_url(blk, feed_type):
            return blk.URL_FORMAT.format(blk.queries[0])
        # default feed type
        blk._prepare_url()
        self.assertEqual(blk.url, prepare_url(blk, 'feed'))
        # # posts
        # blk.feed_type = FeedType.POSTS
        # blk._prepare_url()
        # self.assertEqual(blk.url, prepare_url(blk, 'posts'))
        # # posts
        # blk.feed_type = FeedType.TAGGED
        # blk._prepare_url()
        # self.assertEqual(blk.url, prepare_url(blk, 'tagged'))
        # # posts
        # blk.feed_type = FeedType.PROMOTABLE_POSTS
        # blk._prepare_url()
        # self.assertEqual(blk.url, prepare_url(blk, 'promotable_posts'))

    def signals_notified(self, signals, output_id='default'):
        self.last_notified[output_id].extend(signals)

    def test_pass(self):
        pass

    def test_process_signals(self):
        blk = SubredditFeed()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal()])
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(self.last_notified['default'][0].to_dict(), {})
