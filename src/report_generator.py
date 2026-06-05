from pathlib import Path


def generate_linkedin_text(summary):

    lines = [line.strip() for line in summary.splitlines() if line.strip()]

    intro = "IT Tech Tracker: tendencias clave de hoy"
    highlights = []

    for line in lines[:4]:
        if line.startswith("-") or line.startswith("*"):
            highlights.append(line)

    if not highlights and lines:
        highlights.append(lines[0])

    linkedin_text = """
IT Tech Tracker: reporte diario de tecnología.

Principales puntos:
"""

    for item in highlights[:5]:
        linkedin_text += f"{item}\n"

    linkedin_text += "\nLee el reporte completo y comparte estos temas con tu red. #Tecnología #IT #Tendencias"

    return linkedin_text.strip()


def generate_html_report(news, summary, linkedin_text):

    html = f"""

    <html>

    <head>

        <title>IT Tech Tracker Report</title>

    </head>

    <body>

        <h1>IT Technology Trends Report</h1>

        <pre>{summary}</pre>

        <hr>

        <h2>Texto sugerido para LinkedIn</h2>

        <pre>{linkedin_text}</pre>

        <hr>

        <h2>Articles</h2>

    """

    for article in news:

        categories = ", ".join(

            article["categories"]
        )

        html += f"""

        <div>

            <h3>{article['title']}</h3>

            <p>

            Categories: {categories}

            </p>

            <a href="{article['link']}">

            {article['link']}

            </a>

            <br><br>

        </div>

        """

    html += """

    </body>

    </html>

    """

    Path(

        "data/report.html"

    ).write_text(

        html,

        encoding="utf-8"
    )

    print(

        "\nHTML generado: data/report.html"
    )
