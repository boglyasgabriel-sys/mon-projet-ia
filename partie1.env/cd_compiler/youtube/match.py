"""
Étape 2 : IDENTIFICATION.
Parmi les candidats de la recherche, on choisit celui qui correspond le
mieux au morceau Spotify, à partir de trois indices combinés :
- proximité du titre (comparaison de texte) ;
- proximité de la durée ;
- chaîne "officielle" (les chaînes auto-générées par YouTube pour un
  artiste se terminent par "- Topic" : signal très fiable).
"""
from dataclasses import dataclass
from difflib import SequenceMatcher

from cd_compiler.models import Track
from cd_compiler.youtube.search import YoutubeCandidate

MIN_ACCEPTABLE_SCORE = 0.55


@dataclass
class MatchResult:
    candidate: YoutubeCandidate | None
    score: float


def _title_similarity(track: Track, candidate: YoutubeCandidate) -> float:
    target = f"{track.primary_artist} {track.title}".lower()
    return SequenceMatcher(None, target, candidate.title.lower()).ratio()


def _duration_bonus(track: Track, candidate: YoutubeCandidate) -> float:
    if candidate.duration_seconds is None:
        return 0.0
    diff = abs(track.duration_seconds - candidate.duration_seconds)
    if diff <= 5:
        return 0.15
    if diff <= 15:
        return 0.05
    if diff > 30:
        return -0.2
    return 0.0


def _channel_bonus(track: Track, candidate: YoutubeCandidate) -> float:
    channel = candidate.channel.lower()
    bonus = 0.0
    if channel.endswith("- topic") or channel.endswith("-topic"):
        bonus += 0.15
    if track.primary_artist.lower() in channel:
        bonus += 0.1
    return bonus


def score_candidate(track: Track, candidate: YoutubeCandidate) -> float:
    return (
        _title_similarity(track, candidate)
        + _duration_bonus(track, candidate)
        + _channel_bonus(track, candidate)
    )


def find_best_match(track: Track, candidates: list[YoutubeCandidate]) -> MatchResult:
    if not candidates:
        return MatchResult(candidate=None, score=0.0)

    scored = [(c, score_candidate(track, c)) for c in candidates]
    best_candidate, best_score = max(scored, key=lambda pair: pair[1])

    if best_score < MIN_ACCEPTABLE_SCORE:
        return MatchResult(candidate=None, score=best_score)  # aucun résultat assez fiable

    return MatchResult(candidate=best_candidate, score=best_score)