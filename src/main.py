from collector import collect_news

from filtering import filter_news

from classifier import classify_news

from summarizer import summarize_news

from exporter import save_report

from report_generator import generate_html_report, generate_linkedin_text

from email_sender import send_email


def main():

    news = collect_news(
        limit_per_feed=5
    )

    print(
        f"\nNoticias originales: {len(news)}"
    )

    filtered_news = filter_news(
        news
    )

    print(
        f"Noticias filtradas: {len(filtered_news)}"
    )

    classified_news = classify_news(
        filtered_news
    )

    print(
        f"Noticias clasificadas: {len(classified_news)}"
    )

    summary = summarize_news(
        classified_news
    )

    linkedin_text = generate_linkedin_text(summary)

    save_report(
        classified_news,
        summary,
        linkedin_text
    )

    generate_html_report(
        classified_news,
        summary,
        linkedin_text
    )

    print(
        "\nTexto sugerido para LinkedIn:\n"
    )

    print(linkedin_text)

    print(
        "\nEnviando correo..."
    )

    send_email()

    print(
        "\n========== RESUMEN ==========\n"
    )

    print(summary)


if __name__ == "__main__":

    main()
