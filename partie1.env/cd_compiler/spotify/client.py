"""
Connexion à l'API Spotify et récupération d'une playlist (métadonnées + morceaux).
spotipy gère pour nous : l'échange OAuth, le rafraîchissement du token,
et la pagination des résultats.
"""
import re

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from cd_compiler.config import load_spotify_config
from cd_compiler.models import Playlist, Track

PLAYLIST_URL_PATTERN = re.compile(r"open\.spotify\.com/playlist/([a-zA-Z0-9]+)")

# Depuis la migration Spotify de février 2026, le champ contenant le morceau
# dans chaque entrée de playlist s'appelle "item" et non plus "track".
# On garde les deux noms possibles pour ne pas re-casser si ça change encore.
TRACK_FIELD_CANDIDATES = ("item", "track")


def extract_playlist_id(playlist_url: str) -> str:
    """Ex: https://open.spotify.com/playlist/37i9dQ...?si=xxx -> 37i9dQ..."""
    match = PLAYLIST_URL_PATTERN.search(playlist_url)
    if not match:
        raise ValueError(f"URL de playlist Spotify invalide : {playlist_url}")
    return match.group(1)


def _extract_track_payload(item: dict) -> dict | None:
    for field_name in TRACK_FIELD_CANDIDATES:
        payload = item.get(field_name)
        if payload is not None:
            return payload
    return None


class SpotifyPlaylistClient:
    def __init__(self):
        config = load_spotify_config()
        auth_manager = SpotifyOAuth(
            client_id=config.client_id,
            client_secret=config.client_secret,
            redirect_uri=config.redirect_uri,
            scope=config.scope,
            cache_path=".spotify_token_cache",
        )
        self._sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_playlist(self, playlist_url: str) -> Playlist:
        playlist_id = extract_playlist_id(playlist_url)
        meta = self._sp.playlist(playlist_id, fields="id,name,owner.display_name")

        tracks: list[Track] = []
        offset, limit = 0, 100

        while True:
            page = self._sp.playlist_items(playlist_id, offset=offset, limit=limit)
            items = page["items"]
            if not items:
                break

            for i, item in enumerate(items):
                t = _extract_track_payload(item)
                if t is None:
                    continue  # morceau supprimé/indisponible : on l'ignore proprement
                tracks.append(Track(
                    position=offset + i,
                    title=t["name"],
                    artists=[a["name"] for a in t["artists"]],
                    album=t["album"]["name"],
                    duration_ms=t["duration_ms"],
                    isrc=t.get("external_ids", {}).get("isrc"),
                    spotify_uri=t["uri"],
                ))

            offset += limit
            if offset >= page.get("total", 0):
                break

        return Playlist(
            spotify_id=meta["id"],
            name=meta["name"],
            owner=meta["owner"]["display_name"],
            tracks=tracks,
        )