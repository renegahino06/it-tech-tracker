KEYWORDS = {

    "ai",
    "artificial intelligence",
    "agent",
    "llm",
    "security",
    "cyber",
    "cloud",
    "platform",
    "devops",
    "kubernetes",
    "docker",
    "mlops",
    "automation",
    "observability",
    "infrastructure",
    "data",
    "gpu",
    "open source",
    "cve",
    "exploit",
    "vulnerability"
}


BLOCK_WORDS = {

    "weekly self promotion",
    "crosspost",
    "humor",
    "offtopic",
    "meme"
}


def filter_news(news):

    filtered = []

    for article in news:

        title = article["title"].lower()

        if any(word in title for word in BLOCK_WORDS):

            continue

        if any(word in title for word in KEYWORDS):

            filtered.append(article)

    return filtered
