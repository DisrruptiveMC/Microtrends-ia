import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import streamlit as st

# Título de la App
st.title("📊 MicroTRENDS IA - Dashboard")

# 1. Función con cache para cargar datos
@st.cache_data
def cargar_scopus():
    try:
        df = pd.read_csv('scopus (8).csv', encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo de Scopus: {e}")
        return pd.DataFrame()

# 2. Cargar y validar
scopus_df = cargar_scopus()
if scopus_df.empty:
    st.stop()

scopus_df.columns = [col.strip().lower() for col in scopus_df.columns]

possible_keywords_cols = ['author keywords', 'author_keywords', 'keywords', 'keyword']
keywords_col = next((col for col in scopus_df.columns if col in possible_keywords_cols), None)

possible_year_cols = ['year', 'publication year']
year_col = next((col for col in scopus_df.columns if col in possible_year_cols), None)

if not keywords_col or not year_col:
    st.warning("⚠️ No se encontraron columnas de keywords o año.")
    st.stop()

# 3. Procesar tendencias
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

# 4. Visualización
st.subheader("📌 Top 20 Keywords")
st.dataframe(pd.DataFrame(top_keywords, columns=["Keyword", "Frecuencia"]))

fig, ax = plt.subplots(figsize=(12, 6))
df_sorted = pd.DataFrame(top_keywords, columns=["Keyword", "Frecuencia"]).sort_values(by="Frecuencia", ascending=True)
ax.barh(df_sorted["Keyword"], df_sorted["Frecuencia"], color='skyblue')
ax.set_title("Top 20 Palabras Clave Más Frecuentes")
st.pyplot(fig)

# 5. Línea de tendencias
st.subheader("📈 Evolución de Tendencias")
fig2, ax2 = plt.subplots(figsize=(14, 7))
sns.lineplot(data=df_trends, x='Year', y='Frecuencia', hue='Keyword', marker='o', ax=ax2)
ax2.set_title("Evolución de las 10 Principales Palabras Clave por Año")
st.pyplot(fig2)

# 6. PDF Export
def exportar_informe_pdf(top_keywords, df_trends):
    from reportlab.lib.utils import ImageReader
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"microtrends_report_{timestamp}.pdf"

    # 1. Generar y guardar las gráficas como imagen
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    df_sorted = pd.DataFrame(top_keywords, columns=["Keyword", "Frecuencia"]).sort_values(by="Frecuencia", ascending=True)
    ax1.barh(df_sorted["Keyword"], df_sorted["Frecuencia"], color='skyblue')
    ax1.set_title("Top 20 Palabras Clave Más Frecuentes")
    img_path1 = "grafico_top_keywords.png"
    fig1.tight_layout()
    fig1.savefig(img_path1)
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(14, 7))
    sns.lineplot(data=df_trends, x='Year', y='Frecuencia', hue='Keyword', marker='o', ax=ax2)
    ax2.set_title("Evolución de las 10 Principales Palabras Clave por Año")
    fig2.tight_layout()
    img_path2 = "grafico_tendencias.png"
    fig2.savefig(img_path2)
    plt.close(fig2)

    # 2. Crear PDF
    c = canvas.Canvas(file_name, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Informe de Microtendencias - IA")
    c.setFont("Helvetica", 12)
    y = 720

    # Texto Top 10
    c.drawString(50, y, "Top 10 Palabras Clave Emergentes:")
    y -= 20
    for word, count in top_keywords[:10]:
        c.drawString(70, y, f"{word}: {count}")
        y -= 20

    # Insertar primera imagen
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "📊 Gráfica: Palabras Clave Más Frecuentes")
    c.drawImage(ImageReader(img_path1), 50, 300, width=500, preserveAspectRatio=True, mask='auto')

    # Insertar segunda imagen
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "📈 Gráfica: Tendencias por Año")
    c.drawImage(ImageReader(img_path2), 50, 300, width=500, preserveAspectRatio=True, mask='auto')

    c.save()

    # 3. Eliminar imágenes temporales
    os.remove(img_path1)
    os.remove(img_path2)

    return file_name

if st.button("📄 Exportar informe como PDF"):
    nombre_pdf = exportar_informe_pdf(top_keywords, df_trends)
    with open(nombre_pdf, "rb") as f:
        st.download_button("⬇️ Descargar Informe PDF", f, file_name=nombre_pdf, mime="application/pdf")
