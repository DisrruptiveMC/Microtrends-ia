import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import streamlit as st

@st.cache_data

import pandas as pd

try:
    scopus_df = pd.read_csv('scopus_consolidado.csv', encoding='utf-8')
    print("✅ Archivo de Scopus cargado con éxito")
except Exception as e:
    print(f"Error al cargar el archivo de Scopus: {e}")
        return pd.DataFrame()

scopus_df = cargar_scopus()

scopus_df.columns = [col.strip().lower() for col in scopus_df.columns]
possible_keywords_cols = ['author keywords', 'author_keywords', 'keywords', 'keyword']
keywords_col = next((col for col in scopus_df.columns if col in possible_keywords_cols), None)
possible_year_cols = ['year', 'publication year']
year_col = next((col for col in scopus_df.columns if col in possible_year_cols), None)

if not keywords_col or not year_col:
    st.warning("⚠️ No se encontraron columnas de keywords o año.")
else:
 
    all_keywords = []
    yearly_keywords = {}

    for _, row in scopus_df.dropna(subset=[keywords_col, year_col]).iterrows():
        try:
            year = int(row[year_col]) if pd.notna(row[year_col]) else None
        except ValueError:
            year = None
        keywords_str = str(row[keywords_col]) if pd.notna(row[keywords_col]) else ""
        keywords = [kw.strip().lower() for kw in keywords_str.split(';') if kw.strip()]
        all_keywords.extend(keywords)
        if year:
            yearly_keywords.setdefault(year, []).extend(keywords)

    keyword_freq = Counter(all_keywords)
    top_keywords = keyword_freq.most_common(20)

    top10_keywords = [kw[0] for kw in top_keywords[:10]]
    trend_data = []
    for year in sorted(yearly_keywords):
        counter = Counter(yearly_keywords[year])
        for keyword in top10_keywords:
            trend_data.append({'Year': year, 'Keyword': keyword, 'Frecuencia': counter.get(keyword, 0)})

    df_trends = pd.DataFrame(trend_data)

    def exportar_informe_pdf(top_keywords, df_trends):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"microtrends_report_{timestamp}.pdf"
        c = canvas.Canvas(file_name, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Informe de Microtendencias - IA")
        c.setFont("Helvetica", 12)
        y = 720
        c.drawString(50, y, "Top 10 Palabras Clave Emergentes:")
        y -= 20
        for word, count in top_keywords[:10]:
            c.drawString(70, y, f"{word}: {count}")
            y -= 20
        y -= 10
        c.drawString(50, y, "Tendencias por Año:")
        y -= 20
        for year in sorted(df_trends['Year'].unique()):
            c.drawString(70, y, f"Año {year}:")
            y -= 20
            for _, row in df_trends[df_trends['Year'] == year].iterrows():
                c.drawString(90, y, f"{row['Keyword']}: {row['Frecuencia']}")
                y -= 15
                if y < 100:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = 750
        c.save()
        return file_name

    if st.button("📄 Exportar informe como PDF"):
        nombre_pdf = exportar_informe_pdf(top_keywords, df_trends)
        with open(nombre_pdf, "rb") as f:
            st.download_button("⬇️ Descargar Informe PDF", f, file_name=nombre_pdf, mime="application/pdf")
