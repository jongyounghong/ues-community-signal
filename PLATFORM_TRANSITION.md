# Reddit platform transition

Reddit's October 8, 2026 changelog announced this public Data API transition:

- October 31, 2026: new public API access requests stop being accepted;
- January 12, 2027: access removal begins for unregistered apps and users;
- March 2027: remaining public Data API access ends.

Official notice:
https://support.reddithelp.com/hc/en-us/articles/54353370049684-Changelog-October-8-2026

Official migration guide:
https://developers.reddit.com/docs/guides/migrate/public-api

The request for this private tool was submitted on October 19, 2026. Submission
is not approval, and any transitional approval is not treated as permission
beyond its stated duration.

No long-term collector will rely on the legacy public OAuth API. A production
implementation requires one of these paths:

1. a Devvit design whose installed-community scope, cross-subreddit access,
   external endpoint/export behavior, storage, and deletion handling are
   explicitly permitted; or
2. a written Reddit exception that identifies the allowed access path, scope,
   retention rules, and validity period.

If neither path exists for a collection date, Reddit coverage is omitted. The
application does not substitute scraping, RSS, unofficial endpoints, or a
neutral/zero signal.
