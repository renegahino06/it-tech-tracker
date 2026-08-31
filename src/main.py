from pathlib import Path
import json

from collector import collect_news
from filtering import filter_news
from classifier import classify_news
from summarizer import summarize_news
from exporter import save_report
from report_generator import (
    generate_html_report,
    generate_linkedin_text,
    generate_x_text,
)
from email_sender import send_email

from ranking import rank_news, select_top_story
from content_generator import build_content_package
from infographic import generate_infographic


def generate_phase1_assets(classified_news):
    """
    Selecciona la noticia más relevante y genera
    los artefactos de la Fase 1:
        - top_story.json
        - infographic.png
    """

    top_story = select_top_story(classified_news)

    if not top_story:
        print("\nNo hay noticias para generar contenido.")
        return None, None

    # Mostrar las 3 noticias con mayor relevancia
    print("\n========== TOP STORIES ==========")

    ranked_news = rank_news(classified_news)

    for article in ranked_news[:3]:
        print(
            f"- [{article['relevance_score']}/100] "
            f"{article['title']}"
        )

    # Crear estructura de contenido
    content = build_content_package(top_story)

    # Crear directorio data si no existe
    Path("data").mkdir(
        parents=True,
        exist_ok=True,
    )

    # Guardar la noticia seleccionada
    with open(
        "data/top_story.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            content,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("\nTop Story:")
    print(
        f"  {content['title']}"
    )

    print(
        f"  Relevancia: "
        f"{content['relevance_score']}/100"
    )

    # Generar infografía
    try:

        infographic_path = generate_infographic(
            content,
            "data/infographic.png",
        )

        print(
            f"\nInfografía generada: "
            f"{infographic_path}"
        )

    except Exception as exc:

        print(
            "\nWARN: no se pudo generar "
            f"la infografía: {exc}"
        )

        # La infografía no debe romper
        # el resto del pipeline.
        infographic_path = None

    return content, infographic_path


def main():

    # ==================================================
    # 1. COLLECT
    # ==================================================

    news = collect_news(
        limit_per_feed=5
    )

    print(
        f"\nNoticias originales: "
        f"{len(news)}"
    )

    # ==================================================
    # 2. FILTER
    # ==================================================

    filtered_news = filter_news(
        news
    )

    print(
        f"Noticias filtradas: "
        f"{len(filtered_news)}"
    )

    # ==================================================
    # 3. CLASSIFY
    # ==================================================

    classified_news = classify_news(
        filtered_news
    )

    print(
        f"Noticias clasificadas: "
        f"{len(classified_news)}"
    )

    # ==================================================
    # 4. SUMMARY
    # ==================================================

    summary = summarize_news(
        classified_news
    )

    # ==================================================
    # 5. SOCIAL CONTENT
    # ==================================================

    linkedin_text = generate_linkedin_text(
        summary
    )

    x_text = generate_x_text(
        classified_news
    )

    # ==================================================
    # 6. PHASE 1
    #    Ranking + Top Story + Infographic
    # ==================================================

    top_story, infographic_path = (
        generate_phase1_assets(
            classified_news
        )
    )

    # ==================================================
    # 7. SAVE ORIGINAL REPORT
    # ==================================================

    save_report(
        classified_news,
        summary,
        linkedin_text,
    )

    # ==================================================
    # 8. GENERATE HTML REPORT
    # ==================================================

    generate_html_report(
        classified_news,
        summary,
        linkedin_text,
        x_text,
        top_story=top_story,
        infographic_path=infographic_path,
    )

    # ==================================================
    # 9. SHOW SOCIAL CONTENT
    # ==================================================

    print(
        "\nTexto sugerido para LinkedIn:\n"
    )

    print(
        linkedin_text
    )

    print(
        "\nTexto sugerido para X:\n"
    )

    print(
        x_text
    )

    # ==================================================
    # 10. SEND EMAIL
    # ==================================================

    print(
        "\nEnviando correo..."
    )

    send_email()

    # ==================================================
    # 11. FINAL SUMMARY
    # ==================================================

    print(
        "\n========== RESUMEN ==========\n"
    )

    print(
        summary
    )


if __name__ == "__main__":
    main()
