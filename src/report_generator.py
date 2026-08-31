from html import escape
from pathlib import Path

from ranking import select_top_story


def generate_linkedin_text(summary: str) -> str:
    """
    Genera texto sugerido para LinkedIn
    a partir del resumen diario.
    """

    lines = [
        line.strip()
        for line in summary.splitlines()
        if line.strip()
    ]

    highlights = [
        line
        for line in lines[:8]
        if line.startswith(("-", "*"))
    ]

    if not highlights and lines:
        highlights.append(lines[0])

    linkedin_text = (
        "IT Tech Tracker: reporte diario de tecnología.\n"
        "Principales puntos:\n"
    )

    for item in highlights[:5]:
        linkedin_text += f"{item}\n"

    linkedin_text += (
        "\nLee el reporte completo y comparte estos temas "
        "con tu red. #Tecnología #IT #Tendencias"
    )

    return linkedin_text.strip()


def generate_x_text(news: list) -> str:
    """
    Genera texto para X utilizando ahora la noticia
    con mayor relevance score.
    """

    if not news:
        return (
            "IT Tech Tracker: hoy no se detectaron "
            "noticias destacadas. #IT #Tecnología"
        )

    selected = select_top_story(news)

    if not selected:
        selected = news[0]

    title = selected.get(
        "title",
        "Noticia destacada",
    )

    link = selected.get(
        "link",
        "",
    )

    categories = ", ".join(
        selected.get(
            "categories",
            [],
        )
    )

    if not categories:
        categories = "IT"

    # Evitar textos demasiado largos
    max_title_length = 140

    if len(title) > max_title_length:
        title = (
            title[: max_title_length - 3]
            .rstrip()
            + "..."
        )

    text = (
        f'IT Tech Tracker: hoy destaca en '
        f'{categories}: "{title}". '
        f'Más detalles: {link} '
        f'#IT #Tecnología'
    )

    return text.strip()


def generate_html_report(
    news: list,
    summary: str,
    linkedin_text: str,
    x_text: str,
    top_story: dict | None = None,
    infographic_path: str | None = None,
) -> None:
    """
    Genera data/report.html.

    Incluye:
      - resumen diario
      - Top Story
      - infografía inline
      - LinkedIn
      - X
      - listado original de artículos
    """

    # ==================================================
    # TOP STORY
    # ==================================================

    top_story_html = ""

    if top_story:

        title = escape(
            top_story.get(
                "title",
                "",
            )
        )

        relevance_score = top_story.get(
            "relevance_score",
            0,
        )

        categories = escape(
            ", ".join(
                top_story.get(
                    "category_labels",
                    [],
                )
            )
        )

        what_happened = escape(
            top_story.get(
                "what_happened",
                "",
            )
        )

        why_it_matters = escape(
            top_story.get(
                "why_it_matters",
                "",
            )
        )

        source_url = escape(
            top_story.get(
                "url",
                "",
            ),
            quote=True,
        )

        top_story_html = f"""
        <hr>

        <h2>🏆 Top Story</h2>

        <h3>{title}</h3>

        <p>
            <strong>Relevancia:</strong>
            {relevance_score}/100
        </p>

        <p>
            <strong>Categorías:</strong>
            {categories}
        </p>

        <p>
            <strong>¿Qué pasó?</strong>
            {what_happened}
        </p>

        <p>
            <strong>¿Por qué importa?</strong>
            {why_it_matters}
        </p>
        """

        if source_url:

            top_story_html += f"""
            <p>
                <a href="{source_url}">
                    Ver artículo original
                </a>
            </p>
            """

    # ==================================================
    # INFOGRAPHIC
    # ==================================================

    infographic_html = ""

    if (
        infographic_path
        and Path(
            infographic_path
        ).exists()
    ):

        infographic_html = """
        <hr>

        <h2>🖼 Infografía automática</h2>

        <p>
            <img
                src="cid:infographic"
                alt="IT Tech Tracker Infographic"
                style="
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                "
            >
        </p>
        """

    # ==================================================
    # HTML HEADER
    # ==================================================

    html = f"""
    <!DOCTYPE html>

    <html lang="es">

    <head>

        <meta charset="utf-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >

        <title>
            IT Technology Trends Report
        </title>

        <style>

            body {{
                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;

                max-width: 1000px;

                margin:
                    0 auto;

                padding:
                    30px;

                color:
                    #222222;

                line-height:
                    1.6;
            }}

            h1 {{
                color:
                    #0d2538;
            }}

            h2 {{
                color:
                    #163f5c;

                margin-top:
                    30px;
            }}

            h3 {{
                color:
                    #333333;
            }}

            pre {{
                white-space:
                    pre-wrap;

                word-wrap:
                    break-word;

                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;

                background:
                    #f5f7f9;

                padding:
                    16px;

                border-radius:
                    6px;
            }}

            .article {{
                padding:
                    15px 0;

                border-bottom:
                    1px solid #dddddd;
            }}

            .categories {{
                font-size:
                    14px;

                color:
                    #666666;
            }}

            a {{
                color:
                    #1473e6;
            }}

        </style>

    </head>

    <body>

        <h1>
            IT Technology Trends Report
        </h1>

        <h2>
            Resumen diario
        </h2>

        <pre>{escape(summary)}</pre>

        {top_story_html}

        {infographic_html}

        <hr>

        <h2>
            Texto sugerido para LinkedIn
        </h2>

        <pre>{escape(linkedin_text)}</pre>

        <hr>

        <h2>
            Texto sugerido para X
        </h2>

        <pre>{escape(x_text)}</pre>

        <hr>

        <h2>
            Articles
        </h2>
    """

    # ==================================================
    # ARTICLES
    # ==================================================

    for article in news:

        article_title = escape(
            article.get(
                "title",
                "",
            )
        )

        article_link = escape(
            article.get(
                "link",
                "",
            ),
            quote=True,
        )

        article_categories = escape(
            ", ".join(
                article.get(
                    "categories",
                    [],
                )
            )
        )

        source = escape(
            article.get(
                "source",
                "",
            )
        )

        html += f"""
        <div class="article">

            <h3>
                {article_title}
            </h3>

            <p class="categories">
                Categories:
                {article_categories}
            </p>
        """

        if source:

            html += f"""
            <p class="categories">
                Source:
                {source}
            </p>
            """

        html += f"""
            <p>
                <a href="{article_link}">
                    {article_link}
                </a>
            </p>

        </div>
        """

    # ==================================================
    # FOOTER
    # ==================================================

    html += """

        <hr>

        <p
            style="
                color: #777777;
                font-size: 12px;
            "
        >
            Generated automatically by
            IT Tech Tracker.
        </p>

    </body>

    </html>
    """

    # ==================================================
    # WRITE FILE
    # ==================================================

    Path(
        "data"
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    Path(
        "data/report.html"
    ).write_text(
        html,
        encoding="utf-8",
    )

    print(
        "\nHTML generado: "
        "data/report.html"
    )
