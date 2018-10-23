SubredditFeed
=============
Polls the `new` Reddit feed (https://www.reddit.com/r/all/new.json) and returns the most recent posts from each specified (queried) subreddit.  Can use `all` to get all Reddit posts.

Properties
----------
- **creds**: Reddit API credentials.
- **include_query**: If not None, the endpoint for this request, from queries, will be stored in this attribute of the outgoing signal.
- **polling_interval**: How often reddit is polled. A new request will be made for every member of queries at the polling_interval.
- **queries**: List of subreddits to poll.
- **retry_interval**: When a request to reddit fails, wait this many seconds before attempting a retry.
- **retry_limit**: The maximum number of retries to attempt for each request.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Creates a new signal for each Reddit post. Every field on the Post will become a signal attribute. Details about the Reddit Posts can be found [here](https://github.com/reddit/reddit/wiki/JSON#link-implements-votable--created).

Commands
--------
None

Dependencies
------------
requests

Output Example
--------------
The following is a sample of commonly included attributes, but note that not all will be included on every signal:
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

