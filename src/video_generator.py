"""Video informativo de la noticia principal (voz + infografía)."""

import asyncio
import shutil
import subprocess
from pathlib import Path

import edge_tts


VOICE = "es-MX-DaliaNeural"


def build_script(content):
    labels = content.get("category_labels", [])

    parts = [
        f"Noticia del día en tecnología: {content.get('title', '')}.",
    ]

    if labels:
        parts.append(
            "Temas: " + ", ".join(labels) + "."
        )

    parts.append(content.get("why_it_matters", ""))

    recommendations = content.get("recommendations", [])

    if recommendations:
        parts.append(
            "Recomendaciones: " + " ".join(recommendations)
        )

    parts.append(
        "Sigue IT Tech Tracker para más noticias de tecnología."
    )

    return " ".join(part for part in parts if part)


async def _synthesize(text, output_path):

    communicate = edge_tts.Communicate(text, VOICE)

    await communicate.save(str(output_path))


def generate_narration(text, output_path):

    asyncio.run(_synthesize(text, output_path))

    return output_path


def build_video(image_path, audio_path, output_path):

    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg no está instalado o no está en el PATH")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )

    return output_path


def generate_video(
    content,
    infographic_path,
    output_dir="data",
):

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    audio_path = Path(output_dir) / "narration.mp3"
    video_path = Path(output_dir) / "video.mp4"

    generate_narration(
        build_script(content),
        audio_path,
    )

    build_video(
        infographic_path,
        audio_path,
        video_path,
    )

    return video_path
