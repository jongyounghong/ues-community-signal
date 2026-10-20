# Proposed Reddit Data API scope

## Purpose

The sole operator uses a private dashboard on a personal Mac to observe broad,
aggregate discussion patterns around publicly traded companies. The output is
an informational input, not an automated trading system or academic study.
Reddit data and derivatives
are not sold, licensed, shared, redistributed, monetized, or used for an
employer, client, or third party.

This scope was submitted before the October 31, 2026 cutoff for new public
Data API requests. It does not assume that a public OAuth approval, if granted,
would continue beyond Reddit's announced March 2027 public API sunset.

## Requested reads

- Recent public submissions from the approved community allowlist.
- Recent public comments from the same allowlist.
- Only fields needed for bounded aggregation: content ID, creation/edit state,
  timestamp, and public text. Author and profile fields are ignored.

The initial operational cap is 100 recent submissions and 100 recent comments
per approved community per refresh, with no refresh more often than every six
hours. Lower limits supplied by Reddit take precedence.

No collection begins unless Reddit explicitly approves this stated derived-
aggregation use case. A generic client registration or OAuth credential alone
is not treated as approval.

## Explicitly excluded

- Write, vote, message, follow, moderation, or account-automation scopes.
- Private messages or non-public content.
- User profiling, ranking, targeting, sensitive-trait inference, or
  re-identification.
- AI/ML training, fine-tuning, or evaluation.
- Republishing Reddit content or displaying quotes, usernames, profiles,
  permalinks, or original URLs.
- Web scraping, unofficial APIs, access-control circumvention, or multiple
  accounts/clients for additional capacity.

## Rate limits and failure behavior

The adapter will honor Reddit-provided rate-limit headers and `Retry-After`,
back off on errors, and record missing coverage rather than fabricating zero
observations. Access revocation disables collection and triggers deletion of
temporary Reddit material and Reddit-derived aggregates.

The implementation must also satisfy any registration, developer-profile,
app-label, attribution, and deletion mechanism Reddit requires at approval
time. This document does not claim that the scaffold itself is approval or a
complete compliance implementation.
