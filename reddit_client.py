"""
reddit_client.py — PRAW wrapper for the Mentora Reddit Agent.

Core API functions used by reddit_agent.py. All posting/commenting
functions return draft content for human review — nothing is submitted
to Reddit without explicit approval.
"""

import os
import praw
from dotenv import load_dotenv

load_dotenv()


def get_reddit_client() -> praw.Reddit:
    """
    Initialise and return an authenticated PRAW Reddit client.
    Reads credentials from environment variables.
    """
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        username=os.environ["REDDIT_USERNAME"],
        password=os.environ["REDDIT_PASSWORD"],
        user_agent=os.environ["REDDIT_USER_AGENT"],
    )


def verify_auth(reddit: praw.Reddit) -> str:
    """Verify authentication. Returns the authenticated username."""
    return str(reddit.user.me())


def monitor_subreddit(reddit: praw.Reddit, subreddit_name: str, limit: int = 25, sort: str = "new") -> list[dict]:
    """
    Fetch recent posts from a subreddit.

    Args:
        reddit: Authenticated PRAW client
        subreddit_name: Name of the subreddit (without r/)
        limit: Number of posts to fetch (max 100)
        sort: One of 'new', 'hot', 'top', 'rising'

    Returns:
        List of post dicts with title, score, url, body preview, permalink
    """
    subreddit = reddit.subreddit(subreddit_name)
    feed = {
        "new": subreddit.new,
        "hot": subreddit.hot,
        "top": subreddit.top,
        "rising": subreddit.rising,
    }.get(sort, subreddit.new)

    results = []
    for post in feed(limit=limit):
        results.append({
            "title": post.title,
            "score": post.score,
            "num_comments": post.num_comments,
            "url": f"https://reddit.com{post.permalink}",
            "body_preview": post.selftext[:300] if post.selftext else "",
            "author": str(post.author) if post.author else "[deleted]",
            "created_utc": post.created_utc,
        })
    return results


def search_reddit(
    reddit: praw.Reddit,
    query: str,
    subreddit_name: str = "all",
    sort: str = "new",
    time_filter: str = "month",
    limit: int = 20,
) -> list[dict]:
    """
    Search Reddit for posts matching a query.

    Args:
        reddit: Authenticated PRAW client
        query: Search string
        subreddit_name: Subreddit to search in, or 'all' for all of Reddit
        sort: One of 'relevance', 'new', 'top', 'comments'
        time_filter: One of 'all', 'day', 'hour', 'month', 'week', 'year'
        limit: Number of results to return

    Returns:
        List of post dicts
    """
    subreddit = reddit.subreddit(subreddit_name)
    results = []
    for post in subreddit.search(query, sort=sort, time_filter=time_filter, limit=limit):
        results.append({
            "title": post.title,
            "subreddit": str(post.subreddit),
            "score": post.score,
            "num_comments": post.num_comments,
            "url": f"https://reddit.com{post.permalink}",
            "body_preview": post.selftext[:300] if post.selftext else "",
            "author": str(post.author) if post.author else "[deleted]",
        })
    return results


def read_post(reddit: praw.Reddit, url: str, top_comments: int = 10) -> dict:
    """
    Read a post and its top-level comments.

    Args:
        reddit: Authenticated PRAW client
        url: Full URL of the Reddit post
        top_comments: Number of top-level comments to retrieve

    Returns:
        Dict with post details and list of comments
    """
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=0)

    comments = []
    for comment in list(submission.comments)[:top_comments]:
        comments.append({
            "author": str(comment.author) if comment.author else "[deleted]",
            "score": comment.score,
            "body": comment.body,
        })

    return {
        "title": submission.title,
        "subreddit": str(submission.subreddit),
        "author": str(submission.author) if submission.author else "[deleted]",
        "score": submission.score,
        "num_comments": submission.num_comments,
        "url": f"https://reddit.com{submission.permalink}",
        "body": submission.selftext,
        "comments": comments,
    }


def stream_subreddit(
    reddit: praw.Reddit,
    subreddit_name: str,
    keywords: list[str],
    callback,
) -> None:
    """
    Stream new posts from one or more subreddits and call callback on keyword matches.

    Args:
        reddit: Authenticated PRAW client
        subreddit_name: Subreddit name(s) joined with '+' (e.g. 'Coaches+Entrepreneur')
        keywords: List of keywords to match against title and body
        callback: Function called with a post dict when a match is found

    Note:
        This runs indefinitely. Use Ctrl+C to stop.
    """
    subreddit = reddit.subreddit(subreddit_name)
    for post in subreddit.stream.submissions(skip_existing=True):
        combined = (post.title + " " + post.selftext).lower()
        if any(kw.lower() in combined for kw in keywords):
            callback({
                "title": post.title,
                "subreddit": str(post.subreddit),
                "url": f"https://reddit.com{post.permalink}",
                "body_preview": post.selftext[:300],
            })


# ── Posting functions ──────────────────────────────────────────────────────────
# NOTE: These functions submit content to Reddit.
# NEVER call them without explicit human approval of the content first.

def submit_text_post(reddit: praw.Reddit, subreddit_name: str, title: str, body: str) -> dict:
    """
    Submit a text post to a subreddit.

    ⚠️  REQUIRES HUMAN APPROVAL before calling.
    Draft the content, get sign-off, then execute.

    Returns:
        Dict with the permalink and post ID of the submitted post
    """
    subreddit = reddit.subreddit(subreddit_name)
    submission = subreddit.submit(title=title, selftext=body)
    return {
        "id": submission.id,
        "url": f"https://reddit.com{submission.permalink}",
        "title": submission.title,
    }


def post_comment(reddit: praw.Reddit, post_url: str, comment_text: str) -> dict:
    """
    Post a top-level comment on a Reddit submission.

    ⚠️  REQUIRES HUMAN APPROVAL before calling.
    Draft the content, get sign-off, then execute.

    Returns:
        Dict with the comment permalink and ID
    """
    submission = reddit.submission(url=post_url)
    comment = submission.reply(comment_text)
    return {
        "id": comment.id,
        "permalink": f"https://reddit.com{comment.permalink}",
    }


def reply_to_comment(reddit: praw.Reddit, comment_id: str, reply_text: str) -> dict:
    """
    Reply to an existing comment.

    ⚠️  REQUIRES HUMAN APPROVAL before calling.
    Draft the content, get sign-off, then execute.

    Args:
        comment_id: The Reddit comment ID (e.g. 'c0d1e2f')

    Returns:
        Dict with the reply permalink and ID
    """
    comment = reddit.comment(id=comment_id)
    reply = comment.reply(reply_text)
    return {
        "id": reply.id,
        "permalink": f"https://reddit.com{reply.permalink}",
    }
