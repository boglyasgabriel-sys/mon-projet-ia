"""
Étape 3 : OBTENTION du fichier audio.
Ce module ne se demande jamais "est-ce le bon morceau ?" — il télécharge
l'audio de l'URL YouTube qu'on lui donne et le convertit en mp3.
Nécessite ffmpeg installé sur la machine.
"""
from pathlib import Path

import yt_dlp

DOWNLOAD_DIR = Path("data/downloads")


def download_audio(video_url: str, position: int, artist: str, title: str) -> Path:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = f"{position:02d} - {artist} - {title}".replace("/", "-")
    output_template = str(DOWNLOAD_DIR / f"{safe_name}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        # YouTube exige de plus en plus souvent un "PO Token" pour le client web.
        # Le client "tv" n'en a pas besoin actuellement : on l'essaie en premier,
        # avec repli sur les autres si jamais ça change encore.
        "extractor_args": {
            "youtube": {"player_client": ["tv", "android", "web"]}
        },
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return DOWNLOAD_DIR / f"{safe_name}.mp3"