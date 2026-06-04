#!/usr/bin/env python3
"""Fetch the latest uploads from the ChristCentral SF YouTube channel and
write them to _data/sunday_services.json for the Jekyll build to render.

The YouTube Data API key is read from the YOUTUBE_API_KEY environment variable.
It is NEVER hardcoded or committed. In CI it comes from a GitHub Actions secret;
locally, export it in your shell before running:

    export YOUTUBE_API_KEY=...        # do not commit this
    python3 scripts/fetch_sunday_services.py

Only public data (video id, title, publish date, thumbnail) is written out,
so the resulting JSON is safe to commit to a public repo.
"""

import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request

CHANNEL_ID = "UCIMUzH3lANb4CsFwAzsVPTg"  # @ChristCentralSFMedia
WANT = 12  # number of Sunday services to display
SCAN = 30  # how many recent uploads to scan before filtering
TITLE_MATCH = "sunday service"  # only keep uploads whose title contains this
# Matches a service date like (05.31.26) or (5.17.2026) in the title, used to
# collapse duplicate uploads of the same service down to one card.
DATE_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})")
OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "_data",
    "sunday_services.json",
)
API = "https://www.googleapis.com/youtube/v3"


def _ssl_context():
    """Build a TLS context that verifies certificates. Prefer certifi's CA
    bundle when available (works around python.org builds on macOS that can't
    find the system trust store); otherwise fall back to the default context."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


_SSL_CONTEXT = _ssl_context()


def _get(url):
    with urllib.request.urlopen(url, timeout=30, context=_SSL_CONTEXT) as resp:
        return json.load(resp)


def _api(endpoint, params, key):
    params = dict(params, key=key)
    return _get(f"{API}/{endpoint}?{urllib.parse.urlencode(params)}")


def fetch(key):
    # The channel's "uploads" playlist holds every public upload, newest first.
    channel = _api("channels", {"part": "contentDetails", "id": CHANNEL_ID}, key)
    items = channel.get("items")
    if not items:
        raise SystemExit(f"No channel found for id {CHANNEL_ID}")
    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist = _api(
        "playlistItems",
        {"part": "snippet", "playlistId": uploads, "maxResults": SCAN},
        key,
    )

    seen_dates = set()
    videos = []
    for item in playlist.get("items", []):
        snip = item["snippet"]
        title = snip["title"]

        # Keep only Sunday services (drops town halls, retreat sessions, etc.).
        if TITLE_MATCH not in title.lower():
            continue

        # Collapse duplicate uploads of the same service. Uploads come newest
        # first, so the first one we see for a given date is the most recent.
        m = DATE_RE.search(title)
        date_key = m.groups() if m else None
        if date_key and date_key in seen_dates:
            continue
        if date_key:
            seen_dates.add(date_key)

        thumbs = snip.get("thumbnails", {})
        thumb = (
            thumbs.get("maxres")
            or thumbs.get("standard")
            or thumbs.get("high")
            or thumbs.get("medium")
            or thumbs.get("default")
            or {}
        )
        videos.append(
            {
                "id": snip["resourceId"]["videoId"],
                "title": title,
                "published": snip["publishedAt"],
                "thumbnail": thumb.get("url", ""),
            }
        )
        if len(videos) >= WANT:
            break
    return videos


def main():
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        sys.exit("YOUTUBE_API_KEY is not set. Export it (do not commit it) and retry.")

    videos = fetch(key)
    if not videos:
        sys.exit("No videos returned; leaving existing data file untouched.")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {len(videos)} videos to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
