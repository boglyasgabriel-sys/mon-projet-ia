"""
Interface Streamlit : colle une URL de playlist Spotify, suis la progression
du traitement (Spotify -> YouTube -> téléchargement) en direct.
"""
import pandas as pd
import streamlit as st

from cd_compiler.pipeline import run_pipeline_stream

st.set_page_config(page_title="Préparateur de compilation CD", page_icon="💿")
st.title("💿 Préparateur de compilation CD")

playlist_url = st.text_input("URL de la playlist Spotify")
start = st.button("Lancer le traitement", disabled=not playlist_url)

if start:
    progress_bar = st.progress(0)
    status_text = st.empty()
    table_placeholder = st.empty()
    rows = []

    try:
        stream = run_pipeline_stream(playlist_url)

        # Le premier élément renvoyé par le générateur est toujours "playlist_loaded"
        _, playlist, _ = next(stream)
        st.subheader(f"{playlist.name} — {len(playlist.tracks)} morceaux")
        total = len(playlist.tracks)

        for _, playlist, result in stream:
            rows.append({
                "Position": result.track.position + 1,
                "Artiste": result.track.primary_artist,
                "Titre": result.track.title,
                "Statut": result.status,
                "Score": f"{result.match_score:.2f}" if result.match_score else "",
                "Fichier": result.local_filename or "",
            })
            done = len(rows)
            progress_bar.progress(done / total)
            status_text.text(
                f"{done}/{total} — {result.track.primary_artist} - {result.track.title} : {result.status}"
            )
            table_placeholder.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.success("Traitement terminé !")

    except Exception as exc:
        st.error(f"Erreur : {exc}")