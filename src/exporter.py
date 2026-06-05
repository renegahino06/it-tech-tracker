import json
from datetime import datetime


def save_report(news, summary):

    report = {

        "generated_at": datetime.utcnow().isoformat(),

        "news_count": len(news),

        "summary": summary,

        "articles": news
    }

    with open(

        "data/news_report.json",

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            report,

            file,

            indent=4,

            ensure_ascii=False
        )

    print(

        "\nReporte guardado: data/news_report.json"
    )
