"""
Structures de données qui circulent entre les modules.
Une dataclass plutôt qu'un dict simple : l'éditeur peut t'aider à
l'autocomplétion, et une faute de frappe sur un nom de champ devient
une erreur claire plutôt qu'un bug silencieux.
"""
from dataclasses import dataclass, field


@dataclass
class Track:
    position: int              # position dans la playlist (0 = premier morceau)
    title: str
    artists: list[str]
    album: str
    duration_ms: int
    isrc: str | None           # identifiant international du morceau, peut être absent
    spotify_uri: str

    @property
    def duration_seconds(self) -> float:
        return self.duration_ms / 1000

    @property
    def primary_artist(self) -> str:
        return self.artists[0] if self.artists else ""


@dataclass
class Playlist:
    spotify_id: str
    name: str
    owner: str
    tracks: list[Track] = field(default_factory=list)

    @property
    def total_duration_seconds(self) -> float:
        return sum(t.duration_seconds for t in self.tracks)