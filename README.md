RedditBlock
===========

Polls the Reddit feed [https://www.reddit.com/r/<name_of_subreddit>.json](https://www.reddit.com/r/all.json)

Can use `all.json` or `random.json` to get all Reddit posts or get a random subreddit.

Properties
--------------
-   **polling_interval**: How often Reddit is polled. When using more than one query. Each query will be polled at a period equal to the *polling\_interval* times the number of queries.
-   **retry_interval**: When a url request fails, how long to wait before attempting to try again.
-   **queries**: List of subreddits.  

Dependencies
----------------
None

Commands
----------------
None

Input
-------
Any list of signals.

Output
---------
Same list of signals as input.
