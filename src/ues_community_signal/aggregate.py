"""Deterministic, privacy-minimizing aggregation.

Raw text is an input only. It is intentionally absent from ``AggregateRow`` so
downstream persistence cannot accidentally serialize it.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Iterable, Mapping


POSITIVE_WORDS = frozenset({"bullish", "buy", "beat", "growth", "upside", "strong"})
NEGATIVE_WORDS = frozenset({"bearish", "sell", "miss", "decline", "downside", "weak"})
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]*")


@dataclass(frozen=True)
class PublicItem:
    content_id: str
    created_at: datetime
    title: str
    body: str


@dataclass(frozen=True)
class AggregateRow:
    week_start_utc: str
    symbol: str
    mention_count: int | None
    positive_count: int | None
    negative_count: int | None
    mixed_count: int | None
    unclassified_count: int | None
    suppressed: bool


def _direction(text: str) -> str:
    words = {token.lower() for token in TOKEN_RE.findall(text)}
    positive = bool(words & POSITIVE_WORDS)
    negative = bool(words & NEGATIVE_WORDS)
    if positive and negative:
        return "mixed"
    if positive:
        return "positive"
    if negative:
        return "negative"
    return "unclassified"


def _week_start(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("created_at must be timezone-aware")
    utc_value = value.astimezone(timezone.utc)
    monday = utc_value.date().toordinal() - utc_value.weekday()
    return datetime.fromordinal(monday).date().isoformat()


def aggregate_items(
    items: Iterable[PublicItem],
    aliases: Mapping[str, tuple[str, ...]],
    *,
    minimum_publishable_mentions: int = 3,
) -> tuple[AggregateRow, ...]:
    """Return weekly ticker aggregates without retaining text or authors."""

    if minimum_publishable_mentions < 3:
        raise ValueError("sparse-result suppression must require at least three mentions")
    counts: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    seen_ids: set[str] = set()
    for item in items:
        if item.content_id in seen_ids:
            continue
        seen_ids.add(item.content_id)
        text = f"{item.title} {item.body}"
        lowered = text.lower()
        matched = {
            symbol.upper()
            for symbol, names in aliases.items()
            if any(re.search(rf"(?<![A-Za-z0-9]){re.escape(name.lower())}(?![A-Za-z0-9])", lowered) for name in names)
        }
        direction = _direction(text)
        week = _week_start(item.created_at)
        for symbol in matched:
            bucket = counts[(week, symbol)]
            bucket["mention_count"] += 1
            bucket[f"{direction}_count"] += 1

    rows = []
    for (week, symbol), bucket in sorted(counts.items()):
        total = bucket["mention_count"]
        suppressed = total < minimum_publishable_mentions
        rows.append(AggregateRow(
            week_start_utc=week,
            symbol=symbol,
            mention_count=None if suppressed else total,
            positive_count=None if suppressed else bucket["positive_count"],
            negative_count=None if suppressed else bucket["negative_count"],
            mixed_count=None if suppressed else bucket["mixed_count"],
            unclassified_count=None if suppressed else bucket["unclassified_count"],
            suppressed=suppressed,
        ))
    return tuple(rows)
