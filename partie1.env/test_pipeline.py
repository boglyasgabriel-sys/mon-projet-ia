from cd_compiler.pipeline import run_pipeline
url = input("Colle l'URL de ta playlist Spotify : ")
results = run_pipeline(url)

downloaded = sum(1 for r in results if r.status == "downloaded")
skipped = sum(1 for r in results if r.status == "skipped")
print(f"\n{downloaded} téléchargés, {skipped} déjà présents, {len(results) - downloaded - skipped} autres (échec/no_match).")