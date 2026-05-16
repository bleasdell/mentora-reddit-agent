# Mentora Reddit Agent

Reddit API integration for the Mentora marketing agent. Monitors subreddits, searches for ICP conversations, and enables posting and commenting via [PRAW](https://praw.readthedocs.io/).

Built for use with [Hermes Agent](https://github.com/NousResearch/hermes-agent) as part of the Blaze8 / Mentora marketing stack.

---

## What It Does

- **Monitor** subreddits relevant to Mentora's ICP (coaches, course creators, solopreneurs)
- **Search** Reddit for pain points, product category discussions, and competitor mentions
- **Post** text submissions to targeted subreddits (with human approval gate)
- **Comment** and reply to relevant threads (with human approval gate)
- **Stream** new posts in real time for keyword-triggered alerts

---

## Requirements

- Python 3.8+
- A Reddit account
- A Reddit "script" app (see Setup)

```bash
pip install -r requirements.txt
```

---

## Setup

### 1. Create a Reddit Script App

1. Go to https://www.reddit.com/prefs/apps
2. Click **Create App**
3. Select type: **script**
4. Name: `mentora-agent` (or any name)
5. Redirect URI: `http://localhost:8080`
6. Copy the **Client ID** (shown under the app name) and **Client Secret**

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=macos:mentora-agent:v1.0 (by /u/your_reddit_username)
```

**Never commit your `.env` file.** It is listed in `.gitignore`.

---

## Usage

### Verify authentication

```bash
python3 reddit_agent.py --verify
```

### Monitor a subreddit

```bash
python3 reddit_agent.py --monitor Entrepreneur --limit 25
```

### Search Reddit for keywords

```bash
python3 reddit_agent.py --search "course creator burnout" --sort new --limit 20
```

### Search within a specific subreddit

```bash
python3 reddit_agent.py --search "client management" --subreddit smallbusiness --limit 10
```

### Stream new posts matching keywords

```bash
python3 reddit_agent.py --stream "r/Coaches+r/Entrepreneur" --keywords "client management,coaching tool,mentora"
```

### Read a post and its top comments

```bash
python3 reddit_agent.py --read https://www.reddit.com/r/Entrepreneur/comments/xxxx/
```

---

## File Structure

```
mentora-reddit-agent/
├── reddit_agent.py      # Main CLI entry point
├── reddit_client.py     # PRAW wrapper and core API functions
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .gitignore
└── README.md
```

---

## Important Rules

- **All posts and comments require human approval before submission.** This tool drafts content — a human reviews and approves before anything goes live.
- Read each subreddit's rules before posting. Many communities prohibit self-promotion.
- Use an account with established karma. New accounts are often shadowbanned.

---

## License

MIT — see [LICENSE](LICENSE)
