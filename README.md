RedditBlock
===========

Polls the `new` Reddit feed [https://www.reddit.com/r/all/new.json](https://www.reddit.com/r/<subreddit name>/new.json) and returns the most recent posts from each specified (queried) subreddit.

Can use `all` to get all Reddit posts or `random` to get a random subreddit.

Properties
--------------
-   **polling_interval**: How often Reddit is polled. When using more than one query. Each query will be polled at a period equal to the *polling\_interval* times the number of queries.
-   **retry_interval**: When a url request fails, how long to wait before attempting to try again.
-   **queries**: List of subreddits.  
-   **creds**: Reddit API credentials (environmental variables)

Dependencies
----------------
-   [requests](https://pypi.python.org/pypi/requests/)
-   [RESTPolling Block](https://github.com/nio-blocks/http_blocks/blob/master/rest/rest_block.py)

Commands
----------------
None

Input
-------
None

Output
---------
Creates a new signal for each Reddit post. Every field on the Post will become a signal attribute. Details about the Facebook Posts can be found
[here](https://github.com/reddit/reddit/wiki/JSON). The following is a sample of commonly included attributes, but note that not all will be included on every signal:

- domain
- banned_by
- media_embed
- subreddit
- selftext_html
- selftext
- likes
- suggested_sort
- user_reports
- secure_media
- link_flair_text
- id
- from_kind
- gilded
- archived
- clicked
- report_reasons
- author
- media
- score
- approved_by
- over_18
- hidden
- preview
- num_comments
- thumbnail
- subreddit_id
- hide_score
- edited
- link_flair_css_class
- author_flair_css_class
- downs
- secure_media_embed
- saved
- removal_reason
- post_hint
- stickied
- from
- is_self
- from_id
- permalink
- locked
- name
- created
- url
- author_flair_text
- quarantine
- title
- created_utc
- distinguished
- mod_reports
- visited
- num_reports
- ups
