"""
Orchestration complète : Spotify -> YouTube (recherche/identification/téléchargement) -> Supabase.
C'est le seul fichier qui connaît l'enchaînement complet des étapes ;
les autres modules ne se connaissent pas entre eux.
"""
from dataclasses import dataclass

from cd_compiler.models import Playlist, Track
from cd_compiler.spotify.client import SpotifyPlaylistClient
from cd_compiler.youtube.search import search_youtube
from cd_compiler.youtube.match import find_best_match
from cd_compiler.youtube.downloader import download_audio
from cd_compiler.storage.supabase_client import SupabaseStorage


@dataclass
class TrackResult:
    track: Track
    status: str                       # "downloaded" | "no_match" | "failed" | "skipped"
    youtube_url: str | None = None
    match_score: float | None = None
    local_filename: str | None = None
    error_message: str | None = None

def process_track(track: Track, storage: SupabaseStorage, playlist_id: str) -> TrackResult:
    try:
        query = f"{track.primary_artist} {track.title}"
        candidates = search_youtube(query)
        match = find_best_match(track, candidates)

        if match.candidate is None:
            result = TrackResult(track=track, status="no_match")
        else:
            path = download_audio(
                match.candidate.url, track.position, track.primary_artist, track.title
            )
            result = TrackResult(
                track=track,
                status="downloaded",
                youtube_url=match.candidate.url,
                match_score=match.score,
                local_filename=path.name,
            )
    except Exception as exc:
        result = TrackResult(track=track, status="failed", error_message=str(exc))

    storage.save_track_status(playlist_id, result)
    return result



def run_pipeline(playlist_url: str) -> list[TrackResult]:
    spotify_client = SpotifyPlaylistClient()
    storage = SupabaseStorage()

    playlist: Playlist = spotify_client.get_playlist(playlist_url)
    print(f"Playlist : {playlist.name} ({len(playlist.tracks)} morceaux)\n")

    results = []
    for track in playlist.tracks:
        print(f"[{track.position + 1}/{len(playlist.tracks)}] {track.primary_artist} - {track.title}", end=" ")
        result = process_track(track, storage, playlist.spotify_id)
        print(f"-> {result.status}")
        results.append(result)

    return results


def run_pipeline_stream(playlist_url: str):
    spotify_client = SpotifyPlaylistClient()
    storage = SupabaseStorage()

    playlist: Playlist = spotify_client.get_playlist(playlist_url)
    yield ("playlist_loaded", playlist, None)

    for track in playlist.tracks:
        result = process_track(track, storage, playlist.spotify_id)
        yield ("track_processed", playlist, result)