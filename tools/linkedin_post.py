#!/usr/bin/env python3
"""Publish a text post to your own LinkedIn profile via the self-serve
"Share on LinkedIn" product (scope w_member_social). DRY-RUN BY DEFAULT.

    python tools/linkedin_post.py post.md               # prints the payload, sends nothing
    python tools/linkedin_post.py post.md --publish     # actually posts

Environment:
    LINKEDIN_SHARE_TOKEN   member access token (scopes: openid profile w_member_social)
    LINKEDIN_API_VERSION   YYYYMM of a currently supported LinkedIn API version.
                           Versions are retired over time — check the current one in the
                           LinkedIn docs (the Microsoft Learn MCP server in .mcp.json can).

Agent rule (CLAUDE.md §1.3): --publish only after the owner says "publish" for this post.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Callable

MAX_CHARS = 3000
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
POSTS_URL = "https://api.linkedin.com/rest/posts"

# Reserved characters in the Posts API "little text" commentary format.
_RESERVED = re.compile(r"([\\|{}@\[\]()<>#*_~])")


def escape_little_text(text: str) -> str:
    """Escape reserved characters so LinkedIn renders them literally instead of
    truncating the post or interpreting them as mentions/hashtags markup."""
    return _RESERVED.sub(r"\\\1", text)


def build_payload(author_urn: str, text: str) -> dict[str, Any]:
    if not text.strip():
        raise ValueError("post text is empty")
    if len(text) > MAX_CHARS:
        raise ValueError(f"post is {len(text)} chars; LinkedIn allows {MAX_CHARS}")
    return {
        "author": author_urn,
        "commentary": escape_little_text(text),
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [],
                         "thirdPartyDistributionChannels": []},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }


def get_author_urn(token: str, opener: Callable = urllib.request.urlopen) -> str:
    req = urllib.request.Request(USERINFO_URL, headers={"Authorization": f"Bearer {token}"})
    with opener(req, timeout=30) as resp:
        sub = json.load(resp)["sub"]
    return f"urn:li:person:{sub}"


def publish(payload: dict, token: str, version: str,
            opener: Callable = urllib.request.urlopen) -> str:
    req = urllib.request.Request(POSTS_URL, method="POST",
                                 data=json.dumps(payload).encode("utf-8"),
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json",
                                          "LinkedIn-Version": version,
                                          "X-Restli-Protocol-Version": "2.0.0"})
    with opener(req, timeout=30) as resp:
        return resp.headers.get("x-restli-id", "") or f"HTTP {resp.status}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path, help="text/markdown file with the post body")
    ap.add_argument("--publish", action="store_true", help="really post (default: dry run)")
    args = ap.parse_args(argv)

    text = args.file.read_text(encoding="utf-8").strip()
    try:
        preview = build_payload("urn:li:person:<you>", text)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not args.publish:
        print(f"DRY RUN — {len(text)} chars. Payload that would be sent:\n")
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0

    token = os.environ.get("LINKEDIN_SHARE_TOKEN", "").strip()
    version = os.environ.get("LINKEDIN_API_VERSION", "").strip()
    if not token or not re.fullmatch(r"\d{6}", version):
        print("error: set LINKEDIN_SHARE_TOKEN and LINKEDIN_API_VERSION=YYYYMM (see docs/linkedin.md)",
              file=sys.stderr)
        return 2
    post_id = publish(build_payload(get_author_urn(token), text), token, version)
    print(f"published: {post_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
