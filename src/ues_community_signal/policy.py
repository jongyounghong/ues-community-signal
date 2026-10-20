"""Fail-closed access and model-integration policy.

No network request should be constructed before ``require_approved_runtime``
returns successfully. Approval is an external fact supplied by Reddit; this
module never attempts to infer or bypass it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Mapping


APPROVED_COMMUNITIES = (
    "stocks",
    "investing",
    "StockMarket",
    "SecurityAnalysis",
    "ValueInvesting",
    "wallstreetbets",
)

USER_AGENT_RE = re.compile(
    r"^[^:\s()]+:[^:\s()]+:[^\s()]+ \(by /u/[A-Za-z0-9_-]+\)$"
)
CONSERVATIVE_PUBLIC_API_FAIL_CLOSED_DATE = date(2027, 3, 1)


class AccessNotApproved(RuntimeError):
    """Raised when the Reddit approval gate is not explicitly satisfied."""


@dataclass(frozen=True)
class AccessPolicy:
    poll_interval_seconds: int = 6 * 60 * 60
    max_submissions_per_community: int = 100
    max_comments_per_community: int = 100
    temporary_content_id_retention_hours: int = 48
    shadow_only: bool = True
    active_score_contribution: float = 0.0
    initial_future_contribution_cap: float = 0.05

    def validate(self) -> None:
        if self.poll_interval_seconds < 6 * 60 * 60:
            raise ValueError("polling may not run more often than every six hours")
        if not 1 <= self.max_submissions_per_community <= 100:
            raise ValueError("submission cap must be between 1 and 100")
        if not 1 <= self.max_comments_per_community <= 100:
            raise ValueError("comment cap must be between 1 and 100")
        if not 0 <= self.temporary_content_id_retention_hours <= 48:
            raise ValueError("temporary content-ID retention cannot exceed 48 hours")
        if not self.shadow_only or self.active_score_contribution != 0.0:
            raise ValueError("Reddit must start shadow-only with zero contribution")
        if not 0.0 <= self.initial_future_contribution_cap <= 0.05:
            raise ValueError("initial Narrative/Information cap cannot exceed 5%")


def require_approved_runtime(
    environment: Mapping[str, str],
    *,
    today: date | None = None,
) -> None:
    """Fail closed unless transitional approval and OAuth metadata are explicit.

    Reddit announced only the month of the final public API shutdown. This
    scaffold conservatively refuses the legacy path from March 1, 2027 unless
    the operator records a written exception. Devvit uses a separate runtime.
    """

    if environment.get("REDDIT_API_ACCESS_APPROVED", "").strip().lower() != "yes":
        raise AccessNotApproved("explicit Reddit API approval has not been recorded")
    access_path = environment.get("REDDIT_ACCESS_PATH", "").strip().lower()
    if access_path not in {"approved_transitional_public_api", "written_legacy_exception"}:
        raise AccessNotApproved("an explicit approved access path is required")
    current_date = today or date.today()
    if (
        current_date >= CONSERVATIVE_PUBLIC_API_FAIL_CLOSED_DATE
        and access_path != "written_legacy_exception"
    ):
        raise AccessNotApproved(
            "legacy public API access is fail-closed from March 2027 without a written exception"
        )
    if not environment.get("REDDIT_CLIENT_ID", "").strip():
        raise AccessNotApproved("REDDIT_CLIENT_ID is missing")
    user_agent = environment.get("REDDIT_USER_AGENT", "").strip()
    if not USER_AGENT_RE.fullmatch(user_agent):
        raise AccessNotApproved(
            "a truthful unique User-Agent in Reddit's documented "
            "<platform>:<app ID>:<version> (by /u/<username>) format is required"
        )
