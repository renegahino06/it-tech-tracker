from pathlib import Path
import json
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 1000

BACKGROUND = "#071827"
PANEL = "#0D2538"
BORDER = "#28475E"

TEXT = "#F3F7FA"
MUTED = "#9DB2C2"
ACCENT = "#39C6F4"

SUCCESS = "#5BD39A"
WARNING = "#FFB84D"


def get_font(size, bold=False):

    filename = (
        "DejaVuSans-Bold.ttf"
        if bold
        else "DejaVuSans.ttf"
    )

    path = (
        "/usr/share/fonts/truetype/dejavu/"
        + filename
    )

    if os.path.exists(path):
        return ImageFont.truetype(
            path,
            size,
        )

    return ImageFont.load_default()


F_TITLE = get_font(44, True)
F_SECTION = get_font(26, True)
F_BODY = get_font(21)
F_SMALL = get_font(17)
F_TAG = get_font(17, True)
F_SCORE = get_font(50, True)


def draw_panel(draw, box):

    draw.rounded_rectangle(
        box,
        radius=18,
        fill=PANEL,
        outline=BORDER,
        width=2,
    )


def draw_wrapped(
    draw,
    text,
    x,
    y,
    width,
    font,
    fill=TEXT,
):

    lines = textwrap.wrap(
        text,
        width=width,
    )

    draw.multiline_text(
        (x, y),
        "\n".join(lines),
        font=font,
        fill=fill,
        spacing=7,
    )


def draw_tag(
    draw,
    text,
    x,
    y,
):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=F_TAG,
    )

    width = (
        bbox[2]
        - bbox[0]
        + 26
    )

    draw.rounded_rectangle(
        (
            x,
            y,
            x + width,
            y + 38,
        ),
        radius=11,
        fill="#102D43",
        outline=BORDER,
    )

    draw.text(
        (
            x + 13,
            y + 8,
        ),
        text,
        font=F_TAG,
        fill=ACCENT,
    )

    return width + 9


def generate_infographic(
    content,
    output_path="data/infographic.png",
):

    Path(
        output_path
    ).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.new(
        "RGB",
        (
            WIDTH,
            HEIGHT,
        ),
        BACKGROUND,
    )

    draw = ImageDraw.Draw(image)

    # Header

    draw.text(
        (55, 40),
        "IT TECH TRACKER",
        font=F_SMALL,
        fill=ACCENT,
    )

    draw.text(
        (55, 72),
        "Technology Story of the Day",
        font=F_TITLE,
        fill=TEXT,
    )

    draw.text(
        (55, 130),
        "Generación automática · Fase 1",
        font=F_SMALL,
        fill=MUTED,
    )

    # Score

    draw_panel(
        draw,
        (
            1285,
            40,
            1545,
            175,
        ),
    )

    draw.text(
        (1310, 58),
        "RELEVANCIA",
        font=F_SMALL,
        fill=MUTED,
    )

    draw.text(
        (1310, 83),
        f"{content.get('relevance_score', 0)}/100",
        font=F_SCORE,
        fill=SUCCESS,
    )

    # Main story

    draw_panel(
        draw,
        (
            55,
            200,
            1545,
            390,
        ),
    )

    draw.text(
        (85, 225),
        "HISTORIA SELECCIONADA",
        font=F_SECTION,
        fill=TEXT,
    )

    title = content.get(
        "title",
        "Noticia destacada",
    )

    title_font = get_font(
        28 if len(title) > 105 else 34,
        True,
    )

    lines = textwrap.wrap(
        title,
        width=82 if len(title) > 105 else 68,
    )

    draw.multiline_text(
        (85, 270),
        "\n".join(lines[:2]),
        font=title_font,
        fill=TEXT,
        spacing=5,
    )

    x = 85
    y = 350

    for label in content.get(
        "category_labels",
        [],
    )[:4]:

        tag_width = draw_tag(
            draw,
            label,
            x,
            y,
        )

        if x + tag_width > 1450:
            x = 85
            y += 48

            tag_width = draw_tag(
                draw,
                label,
                x,
                y,
            )

        x += tag_width

    # What happened

    draw_panel(
        draw,
        (
            55,
            420,
            780,
            710,
        ),
    )

    draw.text(
        (85, 450),
        "¿QUÉ PASÓ?",
        font=F_SECTION,
        fill=TEXT,
    )

    draw_wrapped(
        draw,
        content.get(
            "what_happened",
            "",
        ),
        85,
        495,
        55,
        F_BODY,
    )

    # Why

    draw_panel(
        draw,
        (
            820,
            420,
            1545,
            710,
        ),
    )

    draw.text(
        (850, 450),
        "¿POR QUÉ IMPORTA?",
        font=F_SECTION,
        fill=TEXT,
    )

    draw_wrapped(
        draw,
        content.get(
            "why_it_matters",
            "",
        ),
        850,
        495,
        52,
        F_BODY,
    )

    # Recommendations

    draw_panel(
        draw,
        (
            55,
            740,
            780,
            945,
        ),
    )

    draw.text(
        (85, 770),
        "RECOMENDACIONES",
        font=F_SECTION,
        fill=TEXT,
    )

    y = 815

    for item in content.get(
        "recommendations",
        [],
    )[:3]:

        draw.ellipse(
            (
                88,
                y + 7,
                101,
                y + 20,
            ),
            fill=WARNING,
        )

        draw_wrapped(
            draw,
            item,
            115,
            y,
            47,
            F_SMALL,
        )

        y += 48

    # Technologies

    draw_panel(
        draw,
        (
            820,
            740,
            1545,
            945,
        ),
    )

    draw.text(
        (850, 770),
        "TECNOLOGÍAS Y CONCEPTOS",
        font=F_SECTION,
        fill=TEXT,
    )

    x = 850
    y = 820

    for term in content.get(
        "technologies",
        [],
    )[:6]:

        bbox = draw.textbbox(
            (0, 0),
            term,
            font=F_TAG,
        )

        tag_width = (
            bbox[2]
            - bbox[0]
            + 26
        )

        if x + tag_width > 1500:
            x = 850
            y += 48

        x += draw_tag(
            draw,
            term,
            x,
            y,
        )

    draw.text(
        (55, 965),
        "IT Tech Tracker · automated content pipeline",
        font=F_SMALL,
        fill=MUTED,
    )

    image.save(
        output_path,
        "PNG",
        optimize=True,
    )

    return output_path
