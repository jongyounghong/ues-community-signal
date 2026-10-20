# UES Community Signal — Reddit access review repository

This repository documents and tests the privacy and access boundaries for a
proposed Reddit Data API adapter used by a private, local, non-commercial
market-discussion dashboard. It is a review scaffold, not a complete collector.

## Current status

**Reddit collection is disabled.** The code fails closed unless the operator
has received explicit Reddit approval and deliberately sets the approval gate.
This repository does not contain OAuth credentials, Reddit data, user data,
portfolio data, or a scraping fallback.

Reddit has not endorsed this application. API access remains disabled unless
and until Reddit explicitly approves this stated use case. The application does
not place trades and is not financial advice.

## Proposed scope

- One approved OAuth client and a truthful, unique User-Agent.
- Read-only access to recent public submissions and public comments.
- At most one refresh every six hours.
- Initial allowlist: `r/stocks`, `r/investing`, `r/StockMarket`,
  `r/SecurityAnalysis`, `r/ValueInvesting`, and `r/wallstreetbets`.
- No posts, comments, votes, messages, follows, moderation actions, private
  messages, advertising, or account automation.
- No HTML scraping, unofficial endpoints, IP/account rotation, or historical
  bulk backfill.

## Data flow

```text
approved OAuth response
  -> bounded in-memory parsing
  -> allowlisted ticker/company matching
  -> deterministic direction rules
  -> sparse-result suppression
  -> bounded-response aggregate counts only
  -> private local dashboard
```

Raw titles, bodies, and comments are not persistence fields; author fields
returned by Reddit are ignored. A keyed content-ID digest may be retained for
at most 48 hours solely for deduplication and permitted reconciliation. Exact
counts are redacted for sparse buckets. Any retained output is limited to
aggregate time buckets, ticker counts, direction proportions, coverage, and
rate-limit status—not quotes, usernames, profiles, permalinks, or original
URLs.

Reddit content is not used to train, fine-tune, or evaluate an AI/ML model and
is not sent to a generative-AI or other third-party model API.

## Investment-model boundary

Community activity starts in `shadow_only` mode with **0% active score
contribution**. If prospective validation later supports promotion, news and
community information must first be de-duplicated into one bounded
Narrative/Information group with an initial maximum contribution of **5%**.
Missing source coverage is omitted, never replaced with zero or a neutral
score.

## Run the policy tests

Python 3.11+ and the standard library are sufficient.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -q
```

The repository intentionally has no command that collects Reddit data before
approval. See [`DATA_HANDLING.md`](DATA_HANDLING.md) and
[`API_SCOPE.md`](API_SCOPE.md) for the review contract.

Network fetching, persistence, and deletion reconciliation are deliberately
not implemented in this scaffold. They must be reviewed against Reddit's then-
current terms and the exact written approval before any collection is enabled.
