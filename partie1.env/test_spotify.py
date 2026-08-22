from cd_compiler.spotify.client import SpotifyPlaylistClient

url = input("Colle l'URL de ta playlist Spotify : ")

client = SpotifyPlaylistClient()
playlist = client.get_playlist(url)

print(f"\nPlaylist : {playlist.name} (par {playlist.owner})")
print(f"{len(playlist.tracks)} morceaux, durée totale : {playlist.total_duration_seconds/60:.1f} min\n")

for track in playlist.tracks:
    print(f"{track.position + 1:>3}. {track.primary_artist} - {track.title}")