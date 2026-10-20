# Data handling and privacy contract

## In-memory only

The following values may exist only while a response is being processed:

- submission or comment text;
- title;
- permalink or original URL.

They are not valid persistence fields and are not written to logs. Author and
profile fields returned by Reddit are ignored rather than parsed into the
application's item model.

## Temporary deduplication state

A keyed HMAC digest of a Reddit content ID may be retained locally for no more
than 48 hours. Its only purposes are duplicate suppression and reconciliation
that is permitted by the final approved design. The key is local, secret,
rotated, and never committed. A digest does not exempt the application from
Reddit's deletion requirements.

## Retained aggregates

Only these derived, community-level values may persist:

- UTC time bucket;
- allowlisted ticker/company category;
- fixed theme category;
- positive, negative, mixed, or unclassified count;
- total mention count and sparse-result suppression state;
- source coverage and rate-limit status.

No per-user row is retained. Exact count fields in sparse cells are stored as
null to reduce disclosure from very small buckets. This is data minimization,
not a claim of formal anonymity or unique-user k-anonymity.

## Edits, deletions, and revocation

This scaffold does not implement persistence or deletion reconciliation. A
production adapter must use a mechanism accepted by Reddit that can remove
deleted or edited content and every affected derivative. If an affected item
cannot be reconciled, the corresponding aggregate must be discarded rather
than retained. No aggregation window may outlive the application's ability to
honor deletion. If access is revoked, collection stops and all temporary
Reddit material and Reddit-derived aggregates are deleted.
