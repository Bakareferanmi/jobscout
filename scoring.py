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


def score_listing(title: str, category_key: str) -> int:
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
    return score
