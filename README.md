RedditBlock
===========

Polls the `new` Reddit feed [https://www.reddit.com/r/all/new.json](https://www.reddit.com/r/<subreddit name>/new.json) and returns the most recent posts from each specified (queried) subreddit.

Can use `all` to get all Reddit posts or `random` to get a random subreddit.

Properties
--------------
-   **polling_interval**: How often Reddit is polled. When using more than one query. Each query will be polled at a period equal to the `polling_interval` times the number of `queries`.
-   **retry_interval**: When a url request fails, how long to wait before attempting to try again.
-   **queries**: List of subreddits.  
-   **creds**: Reddit API credentials.

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
Creates a new signal for each Reddit post. Every field on the Post will become a signal attribute. Details about the Reddit Posts can be found
[here](https://github.com/reddit/reddit/wiki/JSON#link-implements-votable--created). The following is a sample of commonly included attributes, but note that not all will be included on every signal:

```
{
  domain: string,
  banned_by: string,
  subreddit: string,
  selftext: string,
  likes: int,
  user_reports: array,
  id: string, 
  archived: boolean,
  clicked: boolean,
  author: string,
  score: int,
  approved_by: string,
  over_18: boolean,
  hidden: boolean,
  num_comments: int,
  thumbnail: string,
  subreddit_id: string,
  hide_score: boolean,
  edited: boolean,
  saved: boolean,
  name: string,
  created: datetime,
  url: string,
  title: string,
  visited: boolean,
}
```
