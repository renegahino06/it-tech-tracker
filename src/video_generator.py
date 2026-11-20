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
from PIL import Image, ImageDraw

from infographic import ACCENT, BORDER, MUTED, PANEL, TEXT, get_font


VOICE = "es-MX-DaliaNeural"

WIDTH = 1280
HEIGHT = 720
FPS = 25
TICKS_PER_SECOND = 10_000_000
TAIL_SECONDS = 0.8
WORDS_PER_LINE = 7

F_HEADING = get_font(34, True)
F_TITLE = get_font(50, True)
F_BODY = get_font(30)
F_TAGS = get_font(24)


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


def render_card(scene, path):

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (60, 60, WIDTH - 60, 520),
        radius=24,
        fill=PANEL,
        outline=BORDER,
        width=2,
    )

    draw.text((110, 110), scene["heading"], font=F_HEADING, fill=ACCENT)

    y = 180

    for index, paragraph in enumerate(scene["paragraphs"]):

        if scene["style"] == "title" and index == 0:
            font, fill, text = F_TITLE, TEXT, textwrap.fill(paragraph, 34)
        elif scene["style"] == "title":
            font, fill, text = F_TAGS, MUTED, textwrap.fill(paragraph, 60)
        elif scene["style"] == "list":
            font, fill, text = F_BODY, TEXT, textwrap.fill(
                "• " + paragraph, 58, subsequent_indent="   "
            )
        else:
            font, fill, text = F_BODY, TEXT, textwrap.fill(paragraph, 58)

        draw.multiline_text((110, y), text, font=font, fill=fill, spacing=10)

        _, _, _, bottom = draw.multiline_textbbox(
            (110, y), text, font=font, spacing=10
        )

        y = bottom + 28

    image.save(path)


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


def _render_segment(index, duration, is_last, work_dir):

    video_filters = []

    if index == 0:
        video_filters.append("fade=t=in:st=0:d=0.5")

    if is_last:
        fade_out_start = max(duration - 0.4, 0)
        video_filters.append(
            f"fade=t=out:st={fade_out_start:.2f}:d=0.4"
        )

    video_filters.append(f"ass=caption_{index}.ass")

    filter_graph = (
        "[0:v][1:v]overlay="
        "x=0:y='if(lt(t,0.6),(1-t/0.6)*60,0)'[base];"
        f"[base]{','.join(video_filters)}[v];"
        "[2:a]apad[a]"
    )

    _run(
        [
            "ffmpeg", "-y",
            "-t", f"{duration:.2f}",
            "-f", "lavfi",
            "-i", (
                f"gradients=size={WIDTH}x{HEIGHT}:rate={FPS}:"
                f"speed=0.015:seed={index}:"
                "c0=0x071827:c1=0x0D2538:c2=0x1B6E8C:c3=0x071827:"
                "nb_colors=4"
            ),
            "-loop", "1",
            "-t", f"{duration:.2f}",
            "-i", f"card_{index}.png",
            "-i", f"scene_{index}.mp3",
            "-filter_complex", filter_graph,
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
        ],
        cwd=work_dir,
    )


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

        segments = []
        audio_parts = []

        for index, (scene, (audio_path, words)) in enumerate(
            zip(scenes, narrations)
        ):

            duration = _probe_duration(audio_path) + TAIL_SECONDS

            render_card(scene, work_dir / f"card_{index}.png")
            (work_dir / f"caption_{index}.ass").write_text(
                build_ass(words),
                encoding="utf-8",
            )

            _render_segment(
                index,
                duration,
                index == len(scenes) - 1,
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
