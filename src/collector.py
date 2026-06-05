import feedparser


RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://www.reddit.com/r/devops/.rss",
    "https://www.reddit.com/r/artificial/.rss",
    "https://feeds.feedburner.com/TheHackersNews"
]


def collect_news(limit_per_feed=5):

    articles = []

    seen_links = set()

    for feed_url in RSS_FEEDS:

        print(f"Consultando: {feed_url}")

        try:

            feed = feedparser.parse(feed_url)

            if not feed.entries:

                print("Sin resultados")
                continue

            for entry in feed.entries[:limit_per_feed]:

                title = entry.get("title", "").strip()

                link = entry.get("link", "").strip()

                if not link:
                    continue

                if link in seen_links:
                    continue

                seen_links.add(link)

                article = {
                    "title": title,
                    "link": link,
                    "source": feed_url
                }

                articles.append(article)

        except Exception as e:

            print(f"Error leyendo feed: {e}")

    return articles
