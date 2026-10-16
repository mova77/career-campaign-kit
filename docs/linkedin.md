# LinkedIn integration

What LinkedIn actually lets an individual do programmatically (verified October 2026),
and how this kit uses it. See ADR-0002 for the reasoning.

| Need | Route | Who can use it | Tool |
|---|---|---|---|
| Import your own profile | **Data export ZIP** | Everyone | `tools/linkedin_import.py zip` |
| Import your own profile, repeatably | **Member Data Portability API** (DMA) | Members in the EEA + Switzerland | `tools/linkedin_import.py api` |
| Publish a post on your own profile | **Share on LinkedIn** (`w_member_social`) | Everyone, self-serve | `tools/linkedin_post.py` |
| Agent looks up LinkedIn API docs | **Microsoft Learn MCP** | Everyone | `.mcp.json` (loaded by Claude Code) |
| Edit your profile, search jobs, read others' profiles, send messages | — | Partner programmes only | Not supported. Paste text instead |

> **Each person registers their own app.** Tokens belong to one member and only that
> member can consent, so an app or token can't be shared between people. Never commit
> tokens. Keep them in environment variables or your OS keychain.

---

## Route 1 — Data export ZIP (everyone, no developer account)

1. LinkedIn → **Me → Settings & Privacy → Data privacy → Get a copy of your data**.
2. Choose *Download larger data archive* (it includes positions, education and skills). LinkedIn emails a link, usually within 24 hours.
3. Save the ZIP into `profile/sources/` (git-ignored) and run:
   ```bash
   .venv/bin/python tools/linkedin_import.py zip profile/sources/Basic_LinkedInDataExport_*.zip
   ```
4. This writes `profile/sources/linkedin-draft.yaml`, a **draft** in CV schema.
   The `profile-intake` skill walks through it with you line by line.

## Route 2 — Member Data Portability API (EEA + Switzerland)

One-time setup (about 5 minutes):

1. Open <https://www.linkedin.com/developers/apps/new?action=productRequest&productId=826100>.
   This is the *Create app* form with the product request attached.
   - **App name:** e.g. `career-kit-<yourname>`
   - **LinkedIn Page:** select the product's **default Company page**
     (*Member Data Portability (Member) Default Company*). Creating or choosing your own page disqualifies the app.
   - Privacy policy URL: optional for personal use. Logo: any square image.
   - Accept the API Terms → **Create app**.
2. In the app's **Products** tab, confirm **Member Data Portability API (Member)** is
   listed and its terms are accepted. If it isn't there, click *Request access* on it.
3. **Docs and tools → OAuth Token Tools → OAuth Token Generator**: choose your app,
   tick scope `r_dma_portability_self_serve`, *Request access token*, log in, *Allow*.
4. Copy the token into your shell. Don't paste it into chat:
   ```bash
   export LINKEDIN_DMA_TOKEN='…'        # macOS/Linux; on Windows: setx LINKEDIN_DMA_TOKEN "…"
   .venv/bin/python tools/linkedin_import.py api
   ```
   Tokens last about a year. To renew, repeat step 3.

What it fetches: `PROFILE, POSITIONS, EDUCATION, SKILLS, LANGUAGES, CERTIFICATIONS,
PROJECTS, VOLUNTEERING_EXPERIENCES` from
`GET https://api.linkedin.com/rest/memberSnapshotData?q=criteria&domain=<D>` with header
`Linkedin-Version: 202312` (the only version this endpoint accepts). The raw snapshot is
cached to `profile/sources/linkedin-snapshot.json`. Birth date, address and similar
fields are dropped on import.

## Route 3 — Posting (optional)

Useful for an "I'm looking for…" or "back from leave" announcement post.

1. In the same or a separate app, the **Share on LinkedIn** and **Sign In with LinkedIn
   using OpenID Connect** products are self-serve. Add both.
2. Generate a token with scopes `openid profile w_member_social`. Self-serve tokens expire after 60 days.
3. ```bash
   export LINKEDIN_SHARE_TOKEN='…'
   export LINKEDIN_API_VERSION=YYYYMM   # a currently supported version, see the LinkedIn docs
   .venv/bin/python tools/linkedin_post.py campaign/posts/announce.md            # dry run
   .venv/bin/python tools/linkedin_post.py campaign/posts/announce.md --publish  # real
   ```
The agent drafts posts in `campaign/posts/`. It only runs `--publish` after you say "publish" for that specific post.

## What we deliberately don't do

Cookie/session-based "LinkedIn MCP servers" and scrapers log in as you and automate the
site. LinkedIn's User Agreement prohibits this, and accounts using such tools can be
restricted. Losing your LinkedIn account in the middle of a job search is not worth it.
For job ads, paste the text or link, or use another connector (e.g. Indeed) if your
Claude account has one.
