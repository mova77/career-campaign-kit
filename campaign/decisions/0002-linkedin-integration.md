# ADR-0002 — LinkedIn integration via official, member-owned routes only

- **Status:** accepted
- **Date:** 2026-10-16

## Context
LinkedIn is the primary profile and job channel in most markets. As of October 2026:
- There is no official LinkedIn MCP server for member data. LinkedIn's "Develop with MCP"
  page points to the Microsoft Learn MCP server, which serves API documentation, not member data.
- Self-serve API products: Sign In (OpenID Connect), Share on LinkedIn (`w_member_social`),
  and, for EEA/CH members, the Member Data Portability API (`r_dma_portability_self_serve`).
- Profile editing, job search, messaging and reading other members' data require partner approval.
- Unofficial session/cookie-based tools breach the User Agreement and risk account restriction.

## Decision
1. Profile import uses the data-export ZIP (universal) or the DMA snapshot API (EEA/CH).
   Both feed one normaliser, because the API returns the same column-style keys as the CSV export.
2. Imports produce an unverified **draft**. Facts reach `profile.md` only after the owner confirms them.
3. Posting uses Share on LinkedIn. Dry run is the default, and `--publish` needs explicit approval.
4. The Microsoft Learn MCP server is configured in `.mcp.json` so the agent maintains
   integration code against current official docs.
5. No scraping and no session-cookie tools.

## Consequences
- + Zero account risk. Works for every user (ZIP), with automation for EEA/CH users.
- − LinkedIn profile edits remain copy-paste (the `linkedin-optimizer` skill makes this fast).
- − Posting tokens expire every 60 days and need manual renewal.
- Revisit if LinkedIn opens a member-data MCP server or profile-write scopes.
