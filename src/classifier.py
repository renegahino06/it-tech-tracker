import re


CATEGORIES = {

"SECURITY": [
    "cve",
    "exploit",
    "exploits",
    "exploited",
    "vulnerability",
    "vulnerabilities",
    "malware",
    "attack",
    "attacks",
    "security",
    "patch",
    "patches",
    "edr",
    "threat",
    "ransomware"
],

"AI": [
    "ai",
    "llm",
    "agent",
    "agents",
    "artificial intelligence",
    "model",
    "models",
    "genai",
    "gpu",
    "neural",
    "frontier"
],

    "DEVOPS": [
        "devops",
        "platform",
        "docker",
        "kubernetes",
        "ci/cd",
        "infrastructure"
    ],

    "CLOUD": [
        "cloud",
        "aws",
        "azure",
        "gcp"
    ],

    "AUTOMATION": [
        "automation",
        "workflow"
    ]
}


def contains_keyword(text, keyword):

    pattern = r"\b" + re.escape(keyword) + r"\b"

    return re.search(pattern, text) is not None


def classify_news(news):

    classified = []

    for article in news:

        title = article["title"].lower()

        detected_categories = []

        for category, keywords in CATEGORIES.items():

            for keyword in keywords:

                if contains_keyword(title, keyword):

                    detected_categories.append(category)

                    break

        if not detected_categories:

            detected_categories = ["OTHER"]

        article["categories"] = detected_categories

        classified.append(article)

    return classified
