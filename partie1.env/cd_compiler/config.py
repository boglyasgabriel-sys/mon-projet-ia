"""
Centralise la lecture de la configuration (variables d'environnement).
Aucun autre fichier du projet ne doit lire os.environ directement :
tout passe par ici, pour avoir un seul endroit où corriger en cas de souci.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # charge le fichier .env s'il existe à la racine du projet


@dataclass(frozen=True)
class SpotifyConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = "playlist-read-private playlist-read-collaborative"


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Variable d'environnement manquante : {name}. "
            f"Vérifie ton fichier .env (voir .env.example)."
        )
    return value


def load_spotify_config() -> SpotifyConfig:
    return SpotifyConfig(
        client_id=_require_env("SPOTIPY_CLIENT_ID"),
        client_secret=_require_env("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=_require_env("SPOTIPY_REDIRECT_URI"),
    )


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    key: str


def load_supabase_config() -> SupabaseConfig:
    return SupabaseConfig(
        url=_require_env("SUPABASE_URL"),
        key=_require_env("SUPABASE_SERVICE_KEY"),
    )