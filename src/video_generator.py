"""Video informativo de la noticia principal.

Cada escena tiene una tarjeta animada sobre un fondo en movimiento
(filtro `gradients` de ffmpeg) y subtítulos karaoke sincronizados con
la voz de edge-tts.
"""

import asyncio
import re
import shutil
import subprocess
import tempfile
import textwrap
import unicodedata
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

from infographic import ACCENT, BORDER, MUTED, PANEL, TEXT, get_font
from security_guide import build_guide


VOICE = "es-MX-DaliaNeural"

WIDTH = 1280
HEIGHT = 720
FPS = 25
TICKS_PER_SECOND = 10_000_000
TAIL_SECONDS = 0.8
WORDS_PER_LINE = 7

PANEL_RIGHT = 1000
AVATAR_PATH = Path(__file__).resolve().parent.parent / "assets" / "avatar.png"
AVATAR_SIZE = (240, 300)
AVATAR_X = 1020
AVATAR_Y = 110
AVATAR_BOB = 8
SPEECH_GAP = 0.35

F_HEADING = get_font(34, True)
F_TITLE = get_font(50, True)
F_BODY = get_font(30)
F_TAGS = get_font(24)


def _mono_font(size):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consola.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return get_font(size)


F_CODE = _mono_font(24)

CODE_HEADING = "Configuración práctica"

CODE_TOKEN_COLORS = [
    (Token.Comment, "#6B7F95"),
    (Token.Keyword, ACCENT),
    (Token.Name.Builtin, ACCENT),
    (Token.Name.Tag, ACCENT),
    (Token.String, "#A3E635"),
    (Token.Number, "#FBBF24"),
    (Token.Operator, "#94A3B8"),
    (Token.Punctuation, "#94A3B8"),
]
CODE_COLORS = dict(CODE_TOKEN_COLORS)
CODE_PANEL = (60, 60, PANEL_RIGHT, 590)
CODE_BOX = (90, 290, PANEL_RIGHT - 40, 570)
CODE_BG = "#071827"
CODE_TEXT_X = 115
CODE_LINE_Y0 = 305
CODE_LINE_H = 32

CODE_EXAMPLES = {
    "SECURITY": {
        "description": "Revisa actualizaciones y puertos abiertos en Linux.",
        "lang": "bash",
        "lines": [
            "sudo apt update",
            "sudo apt list --upgradable",
            "sudo apt upgrade -y",
            "sudo ss -tulpn",
            "sudo ufw status verbose",
        ],
    },
    "AI": {
        "description": "Prepara un entorno aislado para trabajar con IA.",
        "lang": "bash",
        "lines": [
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "pip install --upgrade pip",
            "pip install openai python-dotenv",
            "cp .env.example .env",
        ],
    },
    "DEVOPS": {
        "description": "Ejecuta un flujo de GitHub Actions todos los días.",
        "lang": "yaml",
        "lines": [
            "on:",
            "  schedule:",
            "    - cron: '0 13 * * *'",
            "  workflow_dispatch:",
            "jobs:",
            "  report:",
            "    runs-on: ubuntu-latest",
            "    steps:",
        ],
    },
    "CLOUD": {
        "description": "Verifica la cuenta y la configuración de la nube.",
        "lang": "bash",
        "lines": [
            "aws configure list",
            "aws sts get-caller-identity",
            "aws s3 ls",
        ],
    },
    "AUTOMATION": {
        "description": "Programa una tarea diaria con cron.",
        "lang": "bash",
        "lines": [
            "crontab -l",
            "# Ejecutar todos los días a las 7:00",
            "0 7 * * * /usr/bin/python3 /opt/app/main.py",
        ],
    },
    "OTHER": {
        "description": "Mantén tu sistema actualizado con comandos básicos.",
        "lang": "bash",
        "lines": [
            "sudo apt update",
            "sudo apt upgrade -y",
            "uname -a",
            "df -h",
        ],
    },
}


def _code_scene(content, guide=None):
    if guide and guide["specific"]:
        description = guide["description"]
        lang = guide["lang"]
        lines = guide["lines"]
    else:
        category = next(
            (c for c in content.get("categories", []) if c in CODE_EXAMPLES),
            "OTHER",
        )
        example = CODE_EXAMPLES[category]
        description = example["description"]
        lang = example["lang"]
        lines = example["lines"]

    return {
        "heading": CODE_HEADING,
        "style": "code",
        "paragraphs": [description],
        "code": {"lang": lang, "lines": lines},
        "narration": (
            f"Configuración de ejemplo: {description} "
            "Revisa cada comando antes de ejecutarlo."
        ),
    }


def _steps_scene(steps):
    return {
        "heading": "Cómo mitigarla",
        "style": "list",
        "paragraphs": steps,
        "narration": "Pasos para mitigar: " + " ".join(steps),
    }


def build_scenes(content):
    title = content.get("title", "")
    labels = content.get("category_labels", [])
    why = content.get("why_it_matters", "")
    recommendations = content.get("recommendations", [])
    source = content.get("source", "")

    title_paragraphs = [title]
    title_narration = f"Noticia del día en tecnología: {title}."

    if labels:
        topics = ", ".join(labels)
        title_paragraphs.append(f"Temas: {topics}")
        title_narration += f" Temas: {topics}."

    scenes = [
        {
            "heading": "Noticia del día en tecnología",
            "style": "title",
            "paragraphs": title_paragraphs,
            "narration": title_narration,
        }
    ]

    if why:
        scenes.append(
            {
                "heading": "¿Por qué importa?",
                "style": "body",
                "paragraphs": [why],
                "narration": why,
            }
        )

    guide = build_guide(content)
    scenes.append(_code_scene(content, guide))

    scenes.append(_diagram_scene(guide["diagram"]))

    if guide["steps"]:
        scenes.append(_steps_scene(guide["steps"]))

    if recommendations:
        scenes.append(
            {
                "heading": "Recomendaciones",
                "style": "list",
                "paragraphs": recommendations,
                "narration": "Recomendaciones: " + " ".join(recommendations),
            }
        )

    scenes.append(
        {
            "heading": "IT Tech Tracker",
            "style": "body",
            "paragraphs": [f"Fuente: {source}"] if source else [],
            "narration": "Sigue IT Tech Tracker para más noticias de tecnología.",
        }
    )

    return scenes


def _diagram_scene(diagram):
    return {
        "heading": diagram["heading"],
        "style": "diagram",
        "paragraphs": [],
        "diagram": diagram,
        "narration": (
            diagram["intro"] + " " + " ".join(diagram["nodes"]) + ". "
            "Puedes frenarlo en cada paso: "
            + ", ".join(diagram["controls"]) + "."
        ),
    }


def _draw_diagram(draw, diagram):
    box_w, box_h, gap = 180, 130, 36
    top = 230

    for index, label in enumerate(diagram["nodes"]):
        x = 110 + index * (box_w + gap)

        draw.rounded_rectangle(
            (x, top, x + box_w, top + box_h),
            radius=16,
            fill=CODE_BG,
            outline=ACCENT,
            width=2,
        )

        text = textwrap.fill(label, 12)
        _, _, text_w, text_h = draw.multiline_textbbox(
            (0, 0), text, font=F_TAGS, spacing=6, align="center"
        )
        draw.multiline_text(
            (x + (box_w - text_w) / 2, top + (box_h - text_h) / 2),
            text,
            font=F_TAGS,
            fill=TEXT,
            spacing=6,
            align="center",
        )

        if index < len(diagram["nodes"]) - 1:
            y = top + box_h // 2
            tip = x + box_w + gap - 6
            draw.line((x + box_w + 6, y, tip, y), fill=ACCENT, width=3)
            draw.polygon(
                [(tip, y), (tip - 10, y - 7), (tip - 10, y + 7)],
                fill=ACCENT,
            )

    step = box_w + gap
    for index, label in enumerate(diagram["controls"]):
        center = 110 + box_w + gap // 2 + index * step
        text = textwrap.fill(label, 16)
        _, _, text_w, _ = draw.multiline_textbbox(
            (0, 0), text, font=F_TAGS, align="center"
        )
        draw.multiline_text(
            (center - text_w / 2, top + box_h + 24),
            text,
            font=F_TAGS,
            fill=MUTED,
            align="center",
        )


def render_card(scene, path):

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (60, 60, PANEL_RIGHT, 520),
        radius=24,
        fill=PANEL,
        outline=BORDER,
        width=2,
    )

    draw.text((110, 110), scene["heading"], font=F_HEADING, fill=ACCENT)

    if scene["style"] == "diagram":
        _draw_diagram(draw, scene["diagram"])
        image.save(path)
        return

    y = 180

    for index, paragraph in enumerate(scene["paragraphs"]):

        if scene["style"] == "title" and index == 0:
            font, fill, text = F_TITLE, TEXT, textwrap.fill(paragraph, 24)
        elif scene["style"] == "title":
            font, fill, text = F_TAGS, MUTED, textwrap.fill(paragraph, 45)
        elif scene["style"] == "list":
            font, fill, text = F_BODY, TEXT, textwrap.fill(
                "• " + paragraph, 46, subsequent_indent="   "
            )
        else:
            font, fill, text = F_BODY, TEXT, textwrap.fill(paragraph, 48)

        draw.multiline_text((110, y), text, font=font, fill=fill, spacing=10)

        _, _, _, bottom = draw.multiline_textbbox(
            (110, y), text, font=font, spacing=10
        )

        y = bottom + 28

    image.save(path)


def _token_color(ttype):

    while ttype is not None:
        if ttype in CODE_COLORS:
            return CODE_COLORS[ttype]
        ttype = ttype.parent

    return TEXT


def _draw_code_line(draw, line, lexer, x, y):

    for ttype, value in lex(line, lexer):
        draw.text((x, y), value, font=F_CODE, fill=_token_color(ttype))
        x += F_CODE.getlength(value)


def render_code_layers(scene, work_dir, index, duration):
    """Devuelve [(png, inicio_s)]: el panel base y cada línea de código
    apareciendo en el momento en que el narrador la menciona."""

    code = scene["code"]

    base = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)

    draw.rounded_rectangle(
        CODE_PANEL, radius=24, fill=PANEL, outline=BORDER, width=2
    )

    for x, color in zip((100, 122, 144), ("#FF5F56", "#FFBD2E", "#27C93F")):
        draw.ellipse((x - 7, 88, x + 7, 102), fill=color)

    draw.text((100, 125), scene["heading"], font=F_HEADING, fill=ACCENT)
    description = textwrap.fill(scene["paragraphs"][0], 44)
    draw.multiline_text(
        (100, 180), description, font=F_BODY, fill=TEXT, spacing=8
    )

    draw.rounded_rectangle(
        CODE_BOX, radius=14, fill=CODE_BG, outline=BORDER, width=2
    )

    base_path = work_dir / f"code_base_{index}.png"
    base.save(base_path)

    layers = [(base_path, 0.0)]

    lines = code["lines"]
    lexer = get_lexer_by_name(code["lang"], stripnl=False, ensurenl=False)
    step = (duration - 1.2) / len(lines)

    for line_index, line in enumerate(lines):

        frame = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        _draw_code_line(
            ImageDraw.Draw(frame),
            line,
            lexer,
            CODE_TEXT_X,
            CODE_LINE_Y0 + line_index * CODE_LINE_H,
        )

        path = work_dir / f"code_{index}_{line_index}.png"
        frame.save(path)
        layers.append((path, 0.8 + line_index * step))

    return layers


def _speech_spans(words):

    spans = []

    for _, start, end in words:
        if spans and start - spans[-1][1] < SPEECH_GAP:
            spans[-1][1] = max(spans[-1][1], end)
        else:
            spans.append([start, end])

    return spans


def _avatar_y_expr(spans):

    if not spans:
        return str(AVATAR_Y)

    speaking = "+".join(
        f"between(t,{start:.2f},{end:.2f})" for start, end in spans
    )

    return f"{AVATAR_Y}-{AVATAR_BOB}*abs(sin(3*PI*t))*({speaking})"


def _ass_time(seconds):

    centis = round(seconds * 100)
    hours, rest = divmod(centis, 360000)
    minutes, rest = divmod(rest, 6000)
    secs, centis = divmod(rest, 100)

    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def _ass_text(text):

    return text.replace("{", "(").replace("}", ")").replace("\\", "")


def build_ass(words):

    lines = [
        words[start:start + WORDS_PER_LINE]
        for start in range(0, len(words), WORDS_PER_LINE)
    ]

    events = []

    for line_index, line in enumerate(lines):

        if line_index + 1 < len(lines):
            line_end = lines[line_index + 1][0][1]
        else:
            line_end = line[-1][2] + 0.6

        karaoke = []

        for word_index, (text, start, end) in enumerate(line):

            if word_index + 1 < len(line):
                duration = line[word_index + 1][1] - start
            else:
                duration = end - start

            centis = max(1, round(duration * 100))
            karaoke.append(f"{{\\k{centis}}}{_ass_text(text)}")

        events.append(
            f"Dialogue: 0,{_ass_time(line[0][1])},{_ass_time(line_end)},"
            f"Default,,0,0,0,,{' '.join(karaoke)}"
        )

    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {WIDTH}",
        f"PlayResY: {HEIGHT}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,DejaVu Sans,40,&H00F4C639,&H00FFFFFF,&H00071827,"
        "&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,80,80,50,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text",
    ]

    return "\n".join(header + events) + "\n"


async def _synthesize_scene(text, audio_path):

    communicate = edge_tts.Communicate(
        text,
        VOICE,
        boundary="WordBoundary",
    )

    words = []

    with open(audio_path, "wb") as audio_file:

        async for chunk in communicate.stream():

            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])

            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / TICKS_PER_SECOND
                end = start + chunk["duration"] / TICKS_PER_SECOND
                words.append((chunk["text"], start, end))

    return words


async def _synthesize_all(scenes, work_dir):

    results = []

    for index, scene in enumerate(scenes):

        audio_path = work_dir / f"scene_{index}.mp3"
        words = await _synthesize_scene(scene["narration"], audio_path)

        results.append((audio_path, words))

    return results


def _require_ffmpeg():

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(
                f"{tool} no está instalado o no está en el PATH"
            )


def _run(command, cwd=None):

    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr[-800:])

    return result


def _probe_duration(path):

    result = _run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )

    return float(result.stdout.strip())


def _render_segment(index, duration, is_last, layers, speech_spans, work_dir):

    video_filters = []

    if index == 0:
        video_filters.append("fade=t=in:st=0:d=0.5")

    if is_last:
        fade_out_start = max(duration - 0.4, 0)
        video_filters.append(
            f"fade=t=out:st={fade_out_start:.2f}:d=0.4"
        )

    video_filters.append(f"ass=caption_{index}.ass")

    avatar_input = len(layers) + 1
    audio_input = len(layers) + 2

    filter_parts = []
    previous = "0:v"

    for layer_index, (_, start) in enumerate(layers):
        input_index = layer_index + 1
        if layer_index == 0:
            options = "x=0:y='if(lt(t,0.6),(1-t/0.6)*60,0)'"
        else:
            options = f"x=0:y=0:enable='gte(t,{start:.2f})'"
        filter_parts.append(
            f"[{previous}][{input_index}:v]overlay={options}[l{layer_index}]"
        )
        previous = f"l{layer_index}"

    filter_parts.append(
        f"[{previous}][{avatar_input}:v]overlay="
        f"x={AVATAR_X}:y='{_avatar_y_expr(speech_spans)}'[la]"
    )
    filter_parts.append(f"[la]{','.join(video_filters)}[v]")
    filter_parts.append(f"[{audio_input}:a]apad[a]")

    command = [
        "ffmpeg", "-y",
        "-t", f"{duration:.2f}",
        "-f", "lavfi",
        "-i", (
            f"gradients=size={WIDTH}x{HEIGHT}:rate={FPS}:"
            f"speed=0.015:seed={index}:"
            "c0=0x071827:c1=0x0D2538:c2=0x1B6E8C:c3=0x071827:"
            "nb_colors=4"
        ),
    ]

    for layer_path, _ in layers:
        command += ["-loop", "1", "-t", f"{duration:.2f}", "-i", layer_path.name]

    command += [
        "-loop", "1",
        "-t", f"{duration:.2f}",
        "-i", "avatar.png",
        "-i", f"scene_{index}.mp3",
        "-filter_complex", ";".join(filter_parts),
        "-map", "[v]",
        "-map", "[a]",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", "192k",
        f"segment_{index}.mp4",
    ]

    _run(command, cwd=work_dir)


def _concat(names, list_path, output_path, work_dir):

    list_path.write_text(
        "\n".join(f"file '{name}'" for name in names) + "\n",
        encoding="utf-8",
    )

    _run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path.name,
            "-c", "copy",
            "-movflags", "+faststart",
            str(output_path),
        ],
        cwd=work_dir,
    )


def _slugify(text, max_length=60):
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit("-", 1)[0]
    return slug or "noticia"


def video_filename(content):
    return f"video_{_slugify(content.get('title', ''))}.mp4"


def generate_video(content, output_dir="data"):

    _require_ffmpeg()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes = build_scenes(content)

    with tempfile.TemporaryDirectory() as tmp:

        work_dir = Path(tmp)

        narrations = asyncio.run(_synthesize_all(scenes, work_dir))

        avatar = Image.open(AVATAR_PATH).convert("RGBA")
        avatar.resize(AVATAR_SIZE, Image.Resampling.LANCZOS).save(
            work_dir / "avatar.png"
        )

        segments = []
        audio_parts = []

        for index, (scene, (audio_path, words)) in enumerate(
            zip(scenes, narrations)
        ):

            duration = _probe_duration(audio_path) + TAIL_SECONDS

            if scene["style"] == "code":
                layers = render_code_layers(scene, work_dir, index, duration)
            else:
                card_path = work_dir / f"card_{index}.png"
                render_card(scene, card_path)
                layers = [(card_path, 0.0)]

            (work_dir / f"caption_{index}.ass").write_text(
                build_ass(words),
                encoding="utf-8",
            )

            _render_segment(
                index,
                duration,
                index == len(scenes) - 1,
                layers,
                _speech_spans(words),
                work_dir,
            )

            segments.append(f"segment_{index}.mp4")
            audio_parts.append(audio_path.name)

        video_path = output_dir / video_filename(content)
        narration_path = output_dir / "narration.mp3"

        _concat(
            segments,
            work_dir / "segments.txt",
            video_path.resolve(),
            work_dir,
        )

        _concat(
            audio_parts,
            work_dir / "audio.txt",
            narration_path.resolve(),
            work_dir,
        )

    return video_path
