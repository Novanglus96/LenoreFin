import os
import re
from pathlib import Path
import praw

FLAIR_ID_MAP = {
    "major": "e3d63234-5dc6-11f0-b36f-0a5798591b21",
    "minor": "0bc44ae2-5dc7-11f0-8a26-9685ac3bddf0",
}


def get_release_type(tag):
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if not match:
        return None
    minor, patch = int(match.group(2)), int(match.group(3))
    if patch != 0:
        return None
    return "major" if minor == 0 else "minor"


def main():
    tag = os.environ["COMMIT_TAG"]
    version = tag.lstrip("v")
    changelog = os.environ["RELEASE_NOTES"]

    release_type = get_release_type(tag)
    flair_id = FLAIR_ID_MAP.get(release_type) if release_type else None
    if not flair_id:
        print(f"⚠️ '{tag}' is a patch release or unrecognized format, skipping Reddit post.")
        return

    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        username=os.environ["REDDIT_USERNAME"],
        password=os.environ["REDDIT_PASSWORD"],
        user_agent="LenoreAppsBot/1.0 by u/LenoreReleaseBot",
    )

    title = f"LenoreFin v{version} Released!"
    body_template = Path("scripts/reddit_post_template.md").read_text()
    body = body_template.format(version=version, changelog=changelog)

    submission = reddit.subreddit("LenoreApps").submit(
        title=title, selftext=body, flair_id=flair_id
    )

    print(f"✅ Posted to Reddit: {submission.shortlink}")


if __name__ == "__main__":
    main()
