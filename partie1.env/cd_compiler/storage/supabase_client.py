"""
Persistance de l'état du traitement dans Supabase.
Permet de savoir quels morceaux ont déjà été traités (et comment),
de reprendre un traitement interrompu, et plus tard d'alimenter une
interface graphique avec l'avancement.
"""
from supabase import create_client, Client

from cd_compiler.config import load_supabase_config


class SupabaseStorage:
    def __init__(self):
        config = load_supabase_config()
        self._client: Client = create_client(config.url, config.key)

    def already_downloaded(self, playlist_id: str, position: int) -> bool:
        response = (
            self._client.table("tracks")
            .select("status")
            .eq("playlist_id", playlist_id)
            .eq("position", position)
            .execute()
        )
        return bool(response.data) and response.data[0]["status"] == "downloaded"

    def save_track_status(self, playlist_id: str, result) -> None:
        payload = {
            "playlist_id": playlist_id,
            "position": result.track.position,
            "artist": result.track.primary_artist,
            "title": result.track.title,
            "status": result.status,
            "youtube_url": result.youtube_url,
            "match_score": result.match_score,
            "local_filename": result.local_filename,
            "error_message": result.error_message,
        }
        self._client.table("tracks").upsert(
            payload, on_conflict="playlist_id,position"
        ).execute()