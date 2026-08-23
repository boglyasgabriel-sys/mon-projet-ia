"""
Étape 1 : RECHERCHE.
Interroge YouTube et renvoie une liste de candidats (métadonnées légères),
sans rien télécharger. On sépare volontairement cette étape de
l'identification : ici on se contente de rassembler des pistes possibles.
"""
from dataclasses import dataclass

import yt_dlp


@dataclass
class YoutubeCandidate:
    video_id: str
    title: str
    channel: str
    duration_seconds: float | None
    url: str


def search_youtube(query: str, max_results: int = 5) -> list[YoutubeCandidate]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,   # métadonnées seulement, pas les formats audio/vidéo : plus rapide, moins de risques de blocage
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)

    candidates = []
    for entry in result.get("entries", []):
        if entry is None:
            continue
        candidates.append(YoutubeCandidate(
            video_id=entry["id"],
            title=entry.get("title", ""),
            channel=entry.get("channel") or entry.get("uploader") or "",
            duration_seconds=entry.get("duration"),
            url=f"https://www.youtube.com/watch?v={entry['id']}",
        ))
    return candidates