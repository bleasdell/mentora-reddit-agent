"""
reddit_agent.py — CLI entry point for the Mentora Reddit Agent.

Usage:
    python3 reddit_agent.py --verify
    python3 reddit_agent.py --monitor Entrepreneur --limit 25
    python3 reddit_agent.py --search "course creator burnout" --sort new --limit 20
    python3 reddit_agent.py --search "client management" --subreddit smallbusiness
    python3 reddit_agent.py --read https://www.reddit.com/r/Entrepreneur/comments/xxxx/
    python3 reddit_agent.py --stream "Coaches+Entrepreneur" --keywords "mentora,client management"
"""

import argparse
import json
import sys

from reddit_client import (
    get_reddit_client,
    verify_auth,
    monitor_subreddit,
    search_reddit,
    read_post,
    stream_subreddit,
)


def print_json(data):
    print(json.dumps(data, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(
        description="Mentora Reddit Agent — monitor, search, and engage on Reddit."
    )

    parser.add_argument("--verify", action="store_true", help="Verify Reddit authentication")
    parser.add_argument("--monitor", metavar="SUBREDDIT", help="Monitor a subreddit for recent posts")
    parser.add_argument("--search", metavar="QUERY", help="Search Reddit for posts matching a query")
    parser.add_argument("--read", metavar="URL", help="Read a post and its top comments")
    parser.add_argument("--stream", metavar="SUBREDDITS", help="Stream new posts (subreddits joined with +)")

    # Options
    parser.add_argument("--subreddit", default="all", help="Subreddit to search within (default: all)")
    parser.add_argument("--sort", default="new", help="Sort order: new, hot, top, rising, relevance (default: new)")
    parser.add_argument("--time", default="month", help="Time filter: all, day, hour, month, week, year (default: month)")
    parser.add_argument("--limit", type=int, default=20, help="Number of results to return (default: 20)")
    parser.add_argument("--comments", type=int, default=10, help="Number of comments to fetch with --read (default: 10)")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords for --stream matching")

    args = parser.parse_args()

    # Require at least one action
    if not any([args.verify, args.monitor, args.search, args.read, args.stream]):
        parser.print_help()
        sys.exit(1)

    reddit = get_reddit_client()

    if args.verify:
        username = verify_auth(reddit)
        print(f"✅  Authenticated as: u/{username}")

    elif args.monitor:
        posts = monitor_subreddit(reddit, args.monitor, limit=args.limit, sort=args.sort)
        print(f"\n📋  r/{args.monitor} — {len(posts)} posts ({args.sort})\n")
        for post in posts:
            print(f"  [{post['score']:>5}] {post['title']}")
            print(f"          {post['url']}")
            if post["body_preview"]:
                print(f"          {post['body_preview'][:120]}...")
            print()

    elif args.search:
        results = search_reddit(
            reddit,
            args.search,
            subreddit_name=args.subreddit,
            sort=args.sort,
            time_filter=args.time,
            limit=args.limit,
        )
        print(f"\n🔍  Search: \"{args.search}\" in r/{args.subreddit} — {len(results)} results\n")
        for post in results:
            print(f"  [r/{post['subreddit']}] {post['title']}")
            print(f"  Score: {post['score']} | Comments: {post['num_comments']}")
            print(f"  {post['url']}")
            if post["body_preview"]:
                print(f"  {post['body_preview'][:120]}...")
            print()

    elif args.read:
        post = read_post(reddit, args.read, top_comments=args.comments)
        print(f"\n📄  {post['title']}")
        print(f"    r/{post['subreddit']} | u/{post['author']} | Score: {post['score']} | Comments: {post['num_comments']}")
        print(f"    {post['url']}\n")
        if post["body"]:
            print(f"Body:\n{post['body']}\n")
        print(f"Top {len(post['comments'])} comments:\n")
        for i, comment in enumerate(post["comments"], 1):
            print(f"  [{i}] u/{comment['author']} (score: {comment['score']})")
            print(f"      {comment['body'][:300]}")
            print()

    elif args.stream:
        keywords = [kw.strip() for kw in args.keywords.split(",") if kw.strip()]
        if not keywords:
            print("Error: --stream requires --keywords")
            sys.exit(1)

        print(f"\n📡  Streaming r/{args.stream} for keywords: {keywords}")
        print("    Press Ctrl+C to stop.\n")

        def on_match(post):
            print(f"  🎯  MATCH: {post['title']}")
            print(f"      r/{post['subreddit']} — {post['url']}")
            if post["body_preview"]:
                print(f"      {post['body_preview'][:150]}...")
            print()

        try:
            stream_subreddit(reddit, args.stream, keywords, callback=on_match)
        except KeyboardInterrupt:
            print("\nStream stopped.")


if __name__ == "__main__":
    main()
