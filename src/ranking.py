"""Relevance ranking for IT Tech Tracker."""

from urllib.parse import urlparse


CATEGORY_WEIGHTS = {
    "SECURITY": 30,
    "AI": 28,
    "DEVOPS": 24,
    "CLOUD": 20,
    "AUTOMATION": 18,
    "OTHER": 8,
}

IMPACT_KEYWORDS = {
    "zero-day": 14,
    "zero day": 14,
    "exploit": 10,
    "exploited": 10,
    "vulnerability": 9,
    "breach": 12,
    "ransomware": 10,
    "attack": 8,
    "critical": 7,
    "agent": 7,
    "prompt injection": 12,
    "reward hacking": 10,
    "data leak": 10,
    "kubernetes": 6,
}

SOURCE_BONUS = {
    "thehackernews.com": 8,
    "bleepingcomputer.com": 8,
    "arstechnica.com": 7,
    "techcrunch.com": 7,
    "theregister.com": 6,
    "github.com": 5,
}


def score_article(article):
    title = article.get("title", "").strip()
    lower = title.lower()
    categories = article.get("categories", [])

    category_score = max(
        (CATEGORY_WEIGHTS.get(c, 0) for c in categories),
        default=0,
    )

    matched_keywords = [
        keyword
        for keyword in IMPACT_KEYWORDS
        if keyword in lower
    ]

    impact_score = sum(
        IMPACT_KEYWORDS[keyword]
        for keyword in matched_keywords
    )

    hostname = (
        urlparse(article.get("link", "")).hostname
        or ""
    ).lower().removeprefix("www.")

    source_score = next(
        (
            bonus
            for domain, bonus in SOURCE_BONUS.items()
            if hostname == domain or hostname.endswith("." + domain)
        ),
        0,
    )

    event_bonus = 5 if any(
        word in lower
        for word in (
            "says",
            "found",
            "discovered",
            "breach",
            "targets",
            "launches",
        )
    ) else 0

    score = min(
        100,
        category_score
        + impact_score
        + source_score
        + event_bonus,
    )

    result = dict(article)

    result["relevance_score"] = score

    result["score_breakdown"] = {
        "category": category_score,
        "impact": impact_score,
        "source": source_score,
        "event": event_bonus,
        "matched_keywords": matched_keywords,
    }

    return result


def rank_news(news):
    return sorted(
        (score_article(article) for article in news),
        key=lambda article: (
            article["relevance_score"],
            len(article.get("categories", [])),
        ),
        reverse=True,
    )


def select_top_story(news):
    ranked = rank_news(news)

    return ranked[0] if ranked else None
