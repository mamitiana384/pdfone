import os
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
import tempfile
import platform
import pandas as pd

st.set_page_config(page_title="Fusion PDF", layout="centered")
st.title("📎 Fusion personnalisée des pages de fichiers PDF")

uploaded_files = st.file_uploader(
    "Importer plusieurs fichiers PDF", type="pdf", accept_multiple_files=True
)

# ✅ Options de sélection
st.subheader("🎯 Choisissez les pages à inclure dans le fichier combiné :")
include_first_last = st.checkbox("Inclure la 1ère et la dernière page")
include_specific_page = st.checkbox("Inclure une page spécifique")
specific_page_number = st.number_input(
    "Numéro de la page spécifique à inclure (ex: 3)", min_value=1, step=1, value=1,
    disabled=not include_specific_page
)

if uploaded_files:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_writer = PdfWriter()
        recap_data = []
        fichiers_vides = []

        for uploaded_file in uploaded_files:
            pdf_bytes = uploaded_file.read()

            # Vérification fichier vide
            if len(pdf_bytes) == 0:
                recap_data.append({
                    "Nom du fichier": uploaded_file.name,
                    "Nombre de pages": 0,
                    "Pages ajoutées": "❌ Fichier vide"
                })
                fichiers_vides.append(uploaded_file.name)
                continue

            # Sauvegarde temporaire
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)

            # Lecture PDF
            reader = PdfReader(file_path)
            nb_pages = len(reader.pages)
            pages_ajoutees = []

            # 1ère et dernière page
            if include_first_last and nb_pages >= 1:
                output_writer.add_page(reader.pages[0])
                pages_ajoutees.append("1")
                if nb_pages >= 2:
                    output_writer.add_page(reader.pages[-1])
                    pages_ajoutees.append(str(nb_pages))

            # Page spécifique
            if include_specific_page:
                if specific_page_number <= nb_pages:
                    output_writer.add_page(reader.pages[specific_page_number - 1])
                    pages_ajoutees.append(str(specific_page_number))
                else:
                    pages_ajoutees.append(f"⚠️ Page {specific_page_number} inexistante")

            # Aucune option cochée → inclure toutes les pages
            if not include_first_last and not include_specific_page:
                for i in range(nb_pages):
                    output_writer.add_page(reader.pages[i])
                pages_ajoutees = [f"1 à {nb_pages}"]

            recap_data.append({
                "Nom du fichier": uploaded_file.name,
                "Nombre de pages": nb_pages,
                "Pages ajoutées": ", ".join(pages_ajoutees)
            })

        # Sauvegarde du PDF combiné
        output_path = os.path.join(temp_dir, "pdf_combiné.pdf")
        with open(output_path, "wb") as f_out:
            output_writer.write(f_out)

        # Message sur fichiers vides
        if fichiers_vides:
            st.warning(f"{len(fichiers_vides)} fichier(s) vide(s) ignoré(s) : {', '.join(fichiers_vides)}")

        # Résumé
        st.subheader("📊 Résumé des fichiers traités")
        df_recap = pd.DataFrame(recap_data)
        st.dataframe(df_recap, use_container_width=True)

        # Téléchargement
        with open(output_path, "rb") as f_final:
            st.download_button(
                label="📥 Télécharger le fichier combiné",
                data=f_final,
                file_name="pdf_combiné.pdf",
                mime="application/pdf"
            )

        # Impression directe (Windows)
        if platform.system() == "Windows":
            if st.button("🖨️ Imprimer le fichier maintenant"):
                try:
                    os.startfile(output_path, "print")
                    st.success("Impression lancée avec succès.")
                except Exception as e:
                    st.error(f"Erreur d'impression : {e}")
        else:
            st.info("L'impression automatique est disponible uniquement sous Windows.")
