from pathlib import Path


def generate_html_report(news, summary):

    html = f"""

    <html>

    <head>

        <title>IT Tech Tracker Report</title>

    </head>

    <body>

        <h1>IT Technology Trends Report</h1>

        <pre>{summary}</pre>

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
