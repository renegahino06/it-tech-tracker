from pathlib import Path

PRIORITY_ORDER = ["SECURITY", "AI", "DEVOPS", "OTHER"]


def generate_linkedin_text(summary: str) -> str:
    lines = [line.strip() for line in summary.splitlines() if line.strip()]
    intro = "IT Tech Tracker: tendencias clave de hoy"
    highlights = []

    # Tomar bullets de las primeras líneas del resumen
    for line in lines[:4]:
        if line.startswith("-") or line.startswith("*"):
            highlights.append(line)

    # Fallback: al menos una línea si no hay bullets
    if not highlights and lines:
        highlights.append(lines[0])

    linkedin_text = """IT Tech Tracker: reporte diario de tecnología.
Principales puntos:
"""
    for item in highlights[:5]:
        linkedin_text += f"{item}\n"

    linkedin_text += "\nLee el reporte completo y comparte estos temas con tu red. #Tecnología #IT #Tendencias"

    return linkedin_text.strip()


def generate_x_text(news: list) -> str:
    """
    Genera un texto corto para X (Twitter) usando la noticia
    de mayor impacto según PRIORITY_ORDER: SECURITY > AI > DEVOPS > OTHER.
    """
    if not news:
        return "IT Tech Tracker: hoy no se detectaron noticias destacadas. #IT #Tecnología"

    selected = None

    # Buscar en orden de prioridad
    for cat in PRIORITY_ORDER:
        for article in news:
            if cat in article.get("categories", []):
                selected = article
                break
        if selected:
            break

    # Fallback: primera noticia si no coincide ninguna categoría
    if not selected:
        selected = news[0]

    title = selected.get("title", "Noticia destacada")
    link = selected.get("link", "")
    categories = ", ".join(selected.get("categories", [])) or "IT"

    # Recortar título de forma conservadora para evitar pasar el límite
    max_title_len = 140
    if len(title) > max_title_len:
        title = title[: max_title_len - 3].rstrip() + "..."

    x_text = (
        f"IT Tech Tracker: hoy destaca en {categories}: \"{title}\". "
        f"Más detalles: {link} "
        "#IT #Tecnología"
    )

    return x_text.strip()


def generate_html_report(news: list, summary: str, linkedin_text: str, x_text: str) -> None:
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
        <h2>Texto sugerido para X</h2>
        <pre>{x_text}</pre>
        <hr>
        <h2>Articles</h2>
    """

    for article in news:
        categories = ", ".join(article["categories"])
        html += f"""
        <div>
          <h3>{article['title']}</h3>
          <p>Categories: {categories}</p>
          <a href="{article['link']}">{article['link']}</a>
          <br><br><br>
        </div>
        """

    html += """
      </body>
    </html>
    """

    Path("data/report.html").write_text(html, encoding="utf-8")
    print("\nHTML generado: data/report.html")