"""Structured content package for the selected story."""

from datetime import datetime, timezone


CATEGORY_LABELS = {
    "AI": "Inteligencia Artificial",
    "SECURITY": "Ciberseguridad",
    "DEVOPS": "DevOps",
    "CLOUD": "Cloud",
    "AUTOMATION": "Automatización",
    "OTHER": "Tecnología",
}


IMPACTS = {
    "SECURITY":
        "Puede aumentar el riesgo operativo y requiere revisar "
        "vulnerabilidades, exposición y controles.",

    "AI":
        "Muestra que los sistemas de IA requieren límites, "
        "supervisión y controles de seguridad adecuados.",

    "DEVOPS":
        "Puede afectar procesos de desarrollo, despliegue, "
        "observabilidad y operación.",

    "CLOUD":
        "Puede afectar infraestructura, disponibilidad, "
        "costos o controles de seguridad cloud.",

    "AUTOMATION":
        "Refuerza la necesidad de gobernar automatizaciones "
        "y validar acciones de alto impacto.",

    "OTHER":
        "Puede tener implicaciones para equipos técnicos "
        "que adopten esta tecnología.",
}


RECOMMENDATIONS = {
    "SECURITY": [
        "Revisar vulnerabilidades y controles relacionados con el tema.",
        "Validar parches, monitoreo y mecanismos de detección.",
    ],

    "AI": [
        "Definir límites y supervisión para agentes o sistemas automatizados.",
        "Evaluar riesgos de comportamiento inesperado y abuso.",
    ],

    "DEVOPS": [
        "Evaluar el impacto sobre procesos de desarrollo y operación.",
        "Revisar automatización, observabilidad y controles de despliegue.",
    ],

    "CLOUD": [
        "Revisar configuración, permisos y superficie de exposición.",
        "Evaluar impacto sobre costos, disponibilidad y seguridad.",
    ],

    "AUTOMATION": [
        "Documentar los procesos automatizados.",
        "Agregar validaciones antes de acciones de alto impacto.",
    ],

    "OTHER": [
        "Seguir la evolución de la tecnología.",
        "Evaluar su impacto antes de adoptarla en producción.",
    ],
}


TECH_TERMS = [
    "AI Agents",
    "Zero-Day",
    "Exploit",
    "Vulnerability",
    "Prompt Injection",
    "Reward Hacking",
    "Kubernetes",
    "Docker",
    "Cloud",
    "DevOps",
    "LLM",
    "Open Source",
]


def build_content_package(article):

    categories = article.get("categories") or ["OTHER"]

    title = " ".join(
        article.get(
            "title",
            "Noticia destacada",
        ).split()
    )

    technologies = [
        term
        for term in TECH_TERMS
        if term.lower() in title.lower()
    ]

    technologies += [
        CATEGORY_LABELS.get(category, category)
        for category in categories
        if CATEGORY_LABELS.get(category, category)
        not in technologies
    ]

    recommendations = []

    for category in categories:

        for recommendation in RECOMMENDATIONS.get(
            category,
            RECOMMENDATIONS["OTHER"],
        ):

            if recommendation not in recommendations:
                recommendations.append(
                    recommendation
                )

            if len(recommendations) >= 3:
                break

        if len(recommendations) >= 3:
            break

    return {
        "generated_at":
            datetime.now(timezone.utc).isoformat(),

        "title":
            title,

        "url":
            article.get("link", ""),

        "source":
            article.get("source", ""),

        "categories":
            categories,

        "category_labels":
            [
                CATEGORY_LABELS.get(c, c)
                for c in categories
            ],

        "relevance_score":
            article.get("relevance_score", 0),

        "what_happened":
            (
                f"La noticia destaca un evento relevante "
                f"en {', '.join(categories)}: {title}."
            ),

        "why_it_matters":
            " ".join(
                IMPACTS.get(
                    category,
                    IMPACTS["OTHER"],
                )
                for category in categories[:2]
            ),

        "recommendations":
            recommendations[:3],

        "technologies":
            technologies[:6],

        "score_breakdown":
            article.get(
                "score_breakdown",
                {},
            ),
    }
