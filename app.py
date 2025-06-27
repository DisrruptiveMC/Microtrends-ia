import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from io import StringIO
import datetime

st.set_page_config(page_title="MicroTRENDS IA", layout="wide")

st.title("🔍 MicroTRENDS IA - MVP")
st.markdown("Generación automática de microtendencias a partir de datos de Scopus, Reddit y Google Trends.")

with st.sidebar:
    st.header("📂 Cargar Dataset de Scopus")
    uploaded_file = st.file_uploader("Sube un archivo CSV exportado desde Scopus", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df.columns = [col.strip().lower() for col in df.columns]
    possible_keywords_cols = ['author keywords', 'author_keywords', 'keywords', 'keyword']
    possible_year_cols = ['year', 'publication year']
    
    keywords_col = next((col for col in df.columns if col in possible_keywords_cols), None)
    year_col = next((col for col in df.columns if col in possible_year_cols), None)

    if keywords_col and year_col:
        st.success(f"✅ Dataset cargado correctamente. Columnas detectadas: {keywords_col} y {year_col}")

        all_keywords = []
        yearly_keywords = {}

        for _, row in df.dropna(subset=[keywords_col, year_col]).iterrows():
            try:
                year = int(row[year_col]) if pd.notna(row[year_col]) else None
            except ValueError:
                continue
            keywords = [kw.strip().lower() for kw in str(row[keywords_col]).split(';') if kw.strip()]
            all_keywords.extend(keywords)

            if year:
                yearly_keywords.setdefault(year, []).extend(keywords)

        keyword_freq = Counter(all_keywords)
        top_keywords = keyword_freq.most_common(20)
        df_top = pd.DataFrame(top_keywords, columns=['Keyword', 'Frecuencia'])

        st.subheader("📊 Top 20 Palabras Clave Más Frecuentes")
        st.dataframe(df_top, use_container_width=True)

        fig, ax = plt.subplots(figsize=(10, 6))
        df_top.sort_values(by="Frecuencia", ascending=True).plot.barh(x="Keyword", y="Frecuencia", ax=ax, color="skyblue")
        st.pyplot(fig)

        st.subheader("📄 Informe Resumido")
        resumen = f"### Informe MicroIA ({datetime.date.today()})\n\n"
        resumen += f"Se analizaron {len(df)} registros. Las palabras clave más comunes fueron: "
        resumen += ", ".join([kw[0] for kw in top_keywords[:10]]) + "."
        st.markdown(resumen)

        st.download_button(
            label="⬇️ Descargar Informe como .txt",
            data=resumen,
            file_name=f"MicroIA_Informe_{datetime.date.today()}.txt",
            mime="text/plain"
        )

    else:
        st.error("❌ No se encontraron columnas válidas para keywords o año en el archivo.")
else:
    st.info("📌 Carga un archivo CSV desde la barra lateral para comenzar.")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def exportar_informe_pdf(top_keywords, df_trends):
    nombre_archivo = "informe_microtendencias.pdf"
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "📊 Informe de MicroTendencias Emergentes")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 100, "🔝 Top 10 Palabras Clave:")
    c.setFont("Helvetica", 10)
    y = height - 120
    for i, (kw, freq) in enumerate(top_keywords[:10], 1):
        c.drawString(60, y, f"{i}. {kw} ({freq} menciones)")
        y -= 15

    plt.figure(figsize=(8, 4))
    top10_df = pd.DataFrame(top_keywords[:10], columns=["Keyword", "Frecuencia"])
    top10_df_sorted = top10_df.sort_values(by="Frecuencia")
    plt.barh(top10_df_sorted["Keyword"], top10_df_sorted["Frecuencia"], color="skyblue")
    plt.title("Top 10 Keywords")
    plt.tight_layout()
    grafico_path = "grafico_top10.png"
    plt.savefig(grafico_path)
    plt.close()

    c.drawImage(grafico_path, 50, y - 180, width=500, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()

    return nombre_archivo

if st.button("📄 Exportar informe como PDF"):
    nombre_pdf = exportar_informe_pdf(top_keywords, df_trends)
    with open(nombre_pdf, "rb") as f:
        st.download_button("⬇️ Descargar Informe PDF", f, file_name=nombre_pdf, mime="application/pdf")

if st.button("📄 Exportar informe como PDF"):
    nombre_pdf = exportar_informe_pdf(top_keywords, df_trends)
    with open(nombre_pdf, "rb") as f:
        st.download_button("⬇️ Descargar Informe PDF", f, file_name=nombre_pdf, mime="application/pdf")
