import json
from datetime import datetime


def save_results(news, summary):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output = {

        "timestamp": timestamp,

        "news": news,

        "summary": summary
    }

    filename = f"data/report_{timestamp}.json"

    with open(

        filename,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            output,

            file,

            ensure_ascii=False,

            indent=4

        )

    return filename
