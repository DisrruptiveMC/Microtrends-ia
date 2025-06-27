[pip install matplotlib]
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

    # Normalizar nombres de columnas
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
