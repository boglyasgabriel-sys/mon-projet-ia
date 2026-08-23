from cd_compiler.models import Track
from cd_compiler.youtube.search import search_youtube
from cd_compiler.youtube.match import find_best_match
from cd_compiler.youtube.downloader import download_audio

# Un morceau "à la main", pour tester ce module indépendamment de Spotify
track = Track(
    position=0,
    title="Get Lucky",
    artists=["Daft Punk", "Pharrell Williams"],
    album="Random Access Memories",
    duration_ms=248373,
    isrc=None,
    spotify_uri="",
)

query = f"{track.primary_artist} {track.title}"
print(f"Recherche : {query}")
candidates = search_youtube(query)
for c in candidates:
    print(f"  - {c.title} | {c.channel} | {c.duration_seconds}s")

match = find_best_match(track, candidates)
if match.candidate is None:
    print(f"\nAucun résultat assez fiable (meilleur score : {match.score:.2f})")
else:
    print(f"\nMeilleur match (score {match.score:.2f}) : {match.candidate.title}")
    path = download_audio(match.candidate.url, track.position, track.primary_artist, track.title)
    print(f"Téléchargé : {path}")