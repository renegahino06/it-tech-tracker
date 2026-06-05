from collections import Counter


def summarize_news(news):

    if not news:

        return "No hay noticias."

    category_counter = Counter()

    for article in news:

        for category in article["categories"]:

            category_counter[category] += 1

    summary = []

    summary.append("===== TENDENCIAS =====\n")

    for category, count in category_counter.most_common():

        summary.append(
            f"- {category}: {count} noticias"
        )

    summary.append("\n===== TEMAS DETECTADOS =====\n")

    for article in news[:10]:

        summary.append(
            f"* {article['title']}"
        )

    summary.append("\n===== RECOMENDACIONES =====\n")

    if category_counter.get("AI", 0):

        summary.append(
            "- Revisar impacto de AI Agents y automatización"
        )

    if category_counter.get("SECURITY", 0):

        summary.append(
            "- Priorizar gestión de vulnerabilidades"
        )

    if category_counter.get("DEVOPS", 0):

        summary.append(
            "- Evaluar platform engineering y automatización"
        )

    return "\n".join(summary)
