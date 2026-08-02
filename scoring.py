from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from config import CATEGORIES


def matches_category(title: str, category_key: str) -> bool:
    """Hard filter: does this title plausibly belong to the category at all?"""
    cfg = CATEGORIES[category_key]
    t = title.lower()
    if cfg["exclude"] and any(bad in t for bad in cfg["exclude"]):
        return False
    if cfg["must_include_any"] and not any(kw in t for kw in cfg["must_include_any"]):
        return False
    return True


def _parse_posted(posted: str):
    """Best-effort parse of a posted-date string into an aware UTC datetime.
    Sources use different formats (RFC 822 RSS pubDate, ISO 8601, Atom
    'updated', plain dates, unix timestamps). Returns None if none of them fit."""
    if not posted:
        return None
    posted = posted.strip()

    # RFC 822 — RSS pubDate, e.g. "Wed, 02 Aug 2026 10:00:00 GMT"
    try:
        dt = parsedate_to_datetime(posted)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError):
        pass

    # ISO 8601 — remotive, arbeitnow, atom 'updated', etc.
    try:
        dt = datetime.fromisoformat(posted.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    # Plain date only, e.g. "2026-08-01"
    try:
        dt = datetime.strptime(posted[:10], "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    # Unix timestamp as string
    try:
        ts = float(posted)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except ValueError:
        pass

    return None


def recency_bonus(posted: str) -> int:
    """Newer listings score higher: +6 if posted today, decaying linearly
    to 0 by ~14 days old. Unparseable/missing dates get 0 — treated neutrally,
    not penalized, since some sources don't reliably provide one."""
    dt = _parse_posted(posted)
    if dt is None:
        return 0
    age_days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
    if age_days < 0:
        age_days = 0  # future timestamp / clock skew — treat as fresh
    if age_days >= 14:
        return 0
    return round(6 * (1 - age_days / 14))


def score_listing(title: str, category_key: str, posted: str = "") -> int:
    """Higher score = better match. Used only for ranking, not filtering."""
    cfg = CATEGORIES[category_key]
    t = title.lower()
    score = 0
    for kw in cfg["must_include_any"]:
        if kw in t:
            score += 3
    for kw in cfg["level_include"]:
        if kw in t:
            score += 5  # strongly favor listings that explicitly say junior/intern/entry
    score += recency_bonus(posted)
    return score
