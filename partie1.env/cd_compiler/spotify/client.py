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


def extract_playlist_id(playlist_url: str) -> str:
    """Ex: https://open.spotify.com/playlist/37i9dQ...?si=xxx -> 37i9dQ..."""
    match = PLAYLIST_URL_PATTERN.search(playlist_url)
    if not match:
        raise ValueError(f"URL de playlist Spotify invalide : {playlist_url}")
    return match.group(1)


class SpotifyPlaylistClient:
    def __init__(self):
        config = load_spotify_config()
        auth_manager = SpotifyOAuth(
            client_id=config.client_id,
            client_secret=config.client_secret,
            redirect_uri=config.redirect_uri,
            scope=config.scope,
            cache_path=".spotify_token_cache",  # évite de se reconnecter à chaque lancement
        )
        self._sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_playlist(self, playlist_url: str) -> Playlist:
        playlist_id = extract_playlist_id(playlist_url)
        meta = self._sp.playlist(playlist_id, fields="id,name,owner.display_name")

        tracks: list[Track] = []
        offset, limit = 0, 100  # taille de page max de l'API

        while True:
            page = self._sp.playlist_items(
            playlist_id,
            offset=offset,
            limit=limit,
            )
            items = page["items"]
            #print("DEBUG - nombre d'items :", len(items))
            #print("DEBUG - page :", page)
            if not items:
                break

            for i, item in enumerate(items):
                t = item.get("item")
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