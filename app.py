"""Regresión lineal bivariante: PIB per cápita y esperanza de vida (2024).

Trabajo de Estadística II - UCV, Escuela de Estadística y Ciencias Actuariales.
Ejecutar desde la raíz del proyecto:  streamlit run app.py

Todas las tablas y gráficos de la app son capturas de la salida de IBM SPSS
Statistics (carpeta figuras/spss_v6, generadas con spss/regresion_v6.sps).
Lo único que no viene de SPSS es el mapa de la sección 1.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

RAIZ = Path(__file__).resolve().parent
RUTA_CSV = RAIZ / "data" / "pib_esperanza_vida_2024.csv"
FIG = RAIZ / "figuras" / "spss_v6"

st.set_page_config(
    page_title="PIB per cápita y esperanza de vida · Estadística II",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

SECCIONES = [
    "Portada",
    "1. Datos",
    "2. Estadísticas descriptivas",
    "3. Diagrama de dispersión",
    "4. Verificación de supuestos",
    "5. Coeficientes y ecuación",
    "6. Interpretación de a y b",
    "7. Inferencias sobre A y B",
    "8. Intervalos y predicción",
    "9. Inferencias sobre ρ",
    "10. Coeficiente de determinación",
    "11. Análisis de varianza",
    "Conclusiones y fuente",
]

st.markdown(
    """
<style>
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px;}
h1, h2, h3 {font-family: Georgia, 'Times New Roman', serif; color: #16324f;}
h2 {border-bottom: 2px solid #d9d3c5; padding-bottom: .35rem;}
.portada {background: #16324f; color: #fff; border-radius: 12px; padding: 2rem 2.4rem; margin-bottom: 1.2rem;}
.portada .inst {font-size: .8rem; letter-spacing: .12em; text-transform: uppercase; opacity: .85;}
.portada h1 {color: #fff; font-size: 2.2rem; line-height: 1.15; margin: .6rem 0 .4rem; padding: 0;}
.portada .sub {font-size: 1.05rem; opacity: .92;}
.portada .pie {display: flex; gap: 2rem; flex-wrap: wrap; margin-top: 1.3rem; padding-top: .9rem;
  border-top: 1px solid rgba(255,255,255,.3); font-size: .93rem;}
.portada .pie b {display: block; font-size: .7rem; letter-spacing: .1em; text-transform: uppercase; opacity: .75;}
.formula {font-family: Georgia, serif; font-size: 1.15rem; text-align: center; margin: .6rem 0 1rem;}
.pie-pagina {color: #5b6673; font-size: .82rem; border-top: 1px solid #ddd8cc; margin-top: 2.5rem; padding-top: .8rem;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def datos():
    return pd.read_csv(RUTA_CSV)


def spss(nombre, pie=None):
    """Muestra una captura de SPSS a su tamaño natural (sin agrandarla)."""
    ruta = FIG / f"{nombre}.png"
    if not ruta.exists():
        st.warning(f"Falta la captura de SPSS {nombre}.png")
        return
    w, _ = Image.open(ruta).size
    st.image(str(ruta), width=min(w // 2, 1100))
    st.caption(pie or "Salida de IBM SPSS Statistics.")


def formula(texto):
    st.markdown(f"<div class='formula'>{texto}</div>", unsafe_allow_html=True)


df = datos()

with st.sidebar:
    st.markdown("### Estadística II")
    st.caption("Regresión lineal bivariante · UCV")
    seccion = st.radio("Contenido", SECCIONES, label_visibility="collapsed")
    st.divider()
    st.markdown("**Recta estimada**  \nŶ = 70,104 + 0,000177·X  \nr = 0,665 · r² = 0,442")
    st.caption("Allan Arcia y Eddie Palomino  \nProfesoras: Sandra Pinto y Yuraisi Capriles")

# ==========================================================================
if seccion == "Portada":
    st.markdown(
        """
<div class="portada">
  <div class="inst">Universidad Central de Venezuela · Facultad de Ciencias Económicas y Sociales ·
  Escuela de Estadística y Ciencias Actuariales</div>
  <h1>¿Los países más ricos viven más?</h1>
  <div class="sub">Regresión lineal bivariante entre el PIB per cápita y la esperanza de vida al nacer
  en 100 países, año 2024.</div>
  <div class="pie">
    <div><b>Asignatura</b>Estadística II</div>
    <div><b>Autores</b>Allan Arcia · Eddie Palomino</div>
    <div><b>Profesoras</b>Sandra Pinto · Yuraisi Capriles</div>
    <div><b>Fuente</b>Banco Mundial, Indicadores del Desarrollo Mundial</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        spss("g04b_dispersion_ic", "Diagrama de dispersión con la recta de regresión e intervalo de confianza al 95 % (IBM SPSS Statistics).")
    with c2:
        st.subheader("El trabajo en pocas líneas")
        st.markdown(
            """
- **X:** PIB per cápita en US$ corrientes (2024). **Y:** esperanza de vida al nacer en años (2024).
- Recta estimada: **Ŷ = 70,104 + 0,000177·X**. Cada 10.000 dólares de PIB per cápita se asocian con
  unos 1,77 años más de vida.
- La relación es positiva y significativa (z = 8,81; F = 77,632; Sig. < 0,001), pero moderada:
  r = 0,665 y r² = 0,442.
- La nube de puntos se aplana en los países ricos, por eso la recta no cumple bien los supuestos de
  linealidad y normalidad.
- **Venezuela** (US$ 4.244,5) vive 72,67 años; la recta esperaba 70,86.

Todo el procesamiento se hizo en IBM SPSS Statistics y todas las tablas y gráficos de esta app son
capturas de su salida.
""")
        st.caption("Use el índice de la izquierda para recorrer las secciones en el orden del guion.")

# ==========================================================================
elif seccion == "1. Datos":
    st.header("1. Datos")
    st.markdown(
        """
Los datos salen de una sola base oficial, los **Indicadores del Desarrollo Mundial del Banco Mundial**:
el PIB per cápita en dólares corrientes (NY.GDP.PCAP.CD) y la esperanza de vida al nacer
(SP.DYN.LE00.IN), ambos de 2024, descargados el 15/11/2026.

La población son las N = 217 economías que reportan al Banco Mundial (200 tienen los dos indicadores
de 2024). La muestra son **n = 100 países** de todas las regiones y niveles de ingreso, con Venezuela,
las cinco **zonas azules** (Japón, Italia, Grecia, Costa Rica y Estados Unidos) y diez **zonas rojas**
de África Subsahariana con esperanzas de vida muy bajas. La selección fue intencional.
""")
    spss("t01_region", "Composición de la muestra por región (MEANS, IBM SPSS Statistics).")

    st.subheader("Mapa de la muestra")
    opcion = st.radio("Variable del mapa", ["Esperanza de vida", "Nivel de ingreso"], horizontal=True)
    base = dict(locations=df["iso3"], locationmode="ISO-3", marker_line_color="#ffffff", marker_line_width=0.6)
    if opcion == "Esperanza de vida":
        traza = go.Choropleth(
            z=df["esperanza_vida_2024"], colorscale=[[0, "#dbe8f5"], [0.5, "#5b94c9"], [1, "#12365a"]],
            text=df["pais"], hovertemplate="<b>%{text}</b><br>%{z:.2f} años<extra></extra>",
            colorbar=dict(title="Años"), **base)
    else:
        orden = ["Ingreso bajo", "Ingreso mediano bajo", "Ingreso mediano alto", "Ingreso alto"]
        codigo = df["ingreso"].map({v: i for i, v in enumerate(orden)})
        colores = ["#dbe8f5", "#8fb6dd", "#4a82bd", "#12365a"]
        escala = []
        for i, c in enumerate(colores):
            escala += [[i / 4, c], [(i + 1) / 4, c]]
        traza = go.Choropleth(
            z=codigo, zmin=-0.5, zmax=3.5, colorscale=escala,
            text=df["pais"] + "<br>" + df["ingreso"], hovertemplate="<b>%{text}</b><extra></extra>",
            colorbar=dict(title="Ingreso", tickvals=[0, 1, 2, 3],
                          ticktext=["Bajo", "Mediano bajo", "Mediano alto", "Alto"]), **base)
    mapa = go.Figure(traza)
    mapa.update_geos(projection_type="natural earth", showframe=False, showcoastlines=False,
                     showland=True, landcolor="#efece5", showcountries=True, countrycolor="#ffffff",
                     bgcolor="rgba(0,0,0,0)", lataxis_range=[-58, 85])
    mapa.update_layout(height=480, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)")
    mapa.update_traces(colorbar=dict(len=0.7, thickness=14, outlinewidth=0))
    st.plotly_chart(mapa, width="stretch", config={"displayModeBar": False})
    st.caption("Los países en gris claro no forman parte de la muestra.")

    st.subheader("Base de datos")
    tabla = df.rename(columns={"iso3": "ISO3", "pais": "País", "region": "Región", "ingreso": "Ingreso",
                               "grupo": "Grupo", "pib_pc_usd_2024": "PIB per cápita (US$)",
                               "esperanza_vida_2024": "Esperanza de vida (años)"})
    st.dataframe(tabla, width="stretch", height=380, hide_index=True)
    st.download_button("Descargar CSV", RUTA_CSV.read_bytes(), "pib_esperanza_vida_2024.csv", "text/csv")

# ==========================================================================
elif seccion == "2. Estadísticas descriptivas":
    st.header("2. Estadísticas descriptivas")
    spss("t02_estadisticos", "Estadísticos descriptivos (FREQUENCIES, IBM SPSS Statistics).")
    st.markdown(
        """
El **PIB per cápita** es muy disperso y asimétrico: la media (20.178,84 dólares) casi triplica la
mediana, la asimetría es 2,06 y el coeficiente de variación es 140,1 %. Hay muchos países de ingreso
bajo y medio y unos pocos muy ricos (de Afganistán, 416,9 dólares, a Luxemburgo, 137.781,7).

La **esperanza de vida** es mucho menos dispersa (coeficiente de variación de 10,2 %), con media de
73,68 años, mediana de 74,71 y una ligera asimetría negativa (−0,55) que viene de las zonas rojas.
""")
    c1, c2 = st.columns(2)
    with c1:
        spss("g01_hist_pib", "Histograma del PIB per cápita (IBM SPSS Statistics).")
    with c2:
        spss("g02_hist_esperanza", "Histograma de la esperanza de vida (IBM SPSS Statistics).")
    st.subheader("Por nivel de ingreso y por grupo de interés")
    spss("t03_ingreso", "Medias por nivel de ingreso (MEANS, IBM SPSS Statistics).")
    spss("g03_cajas_ingreso", "Diagrama de caja de la esperanza de vida por nivel de ingreso (IBM SPSS Statistics).")
    spss("t04_grupos", "Medias por grupo de interés (MEANS, IBM SPSS Statistics).")
    st.markdown(
        """
La esperanza de vida media sube de 62,5 años (ingreso bajo) a 81,0 años (ingreso alto), pero no en
proporción al dinero: unos 1.600 dólares más entre ingreso bajo y mediano bajo se asocian con 5,5 años
más, mientras que unos 41.700 dólares más entre mediano alto y alto se asocian con 6,4 años. Las zonas
azules promedian 81,9 años y las zonas rojas 59,0.
""")

# ==========================================================================
elif seccion == "3. Diagrama de dispersión":
    st.header("3. Diagrama de dispersión")
    spss("g04b_dispersion_ic", "Diagrama de dispersión con la recta de regresión e intervalo de confianza al 95 % (GGRAPH, IBM SPSS Statistics).")
    st.markdown(
        """
La relación es positiva, pero no sigue una recta. Hasta unos 20.000 dólares la esperanza de vida sube
muy rápido y luego la nube se aplana entre 80 y 85 años. La recta pasa por encima de casi todos los
países pobres, por debajo de muchos de ingreso medio y otra vez por encima de los más ricos.

Las líneas rojas discontinuas son el **intervalo de confianza al 95 % para la media**: es angosto cerca
del PIB medio y se abre hacia los extremos, sobre todo en los PIB altos, donde hay pocos países.

Casos llamativos: Nigeria y Chad viven unos 15 años menos de lo que da la recta, Estados Unidos vive
menos que otros países ricos y Guyana, con casi 30.000 dólares por el auge petrolero, vive 70,3 años.
""")

# ==========================================================================
elif seccion == "4. Verificación de supuestos":
    st.header("4. Verificación de supuestos")
    st.markdown("Usamos los gráficos de residuos del procedimiento REGRESIÓN de SPSS y el estadístico de "
                "Durbin-Watson.")
    st.subheader("Normalidad")
    c1, c2 = st.columns(2)
    with c1:
        spss("g06_pp_zresid", "Gráfico P-P normal del residuo estandarizado (IBM SPSS Statistics).")
    with c2:
        spss("g05_histograma_zresid", "Histograma del residuo estandarizado (IBM SPSS Statistics).")
    st.markdown(
        """
Los puntos del P-P se separan de la diagonal en el centro y el histograma tiene una cola larga a la
izquierda (residuos cercanos a −3, de Nigeria y Chad), así que **los residuos no son normales**.
""")
    st.subheader("Linealidad y homocedasticidad")
    spss("g07_zpred_zresid", "Residuo estandarizado contra pronóstico estandarizado (IBM SPSS Statistics).")
    st.markdown(
        """
- **Linealidad:** los residuos forman un arco, negativos en los extremos y positivos en el centro.
  Junto con el diagrama de dispersión, esto indica que **la relación no es lineal**.
- **Homocedasticidad:** no hay una banda horizontal pareja. La dispersión es mayor en los pronósticos
  bajos (países pobres) que en los altos, así que **la varianza constante es dudosa**.
- **Independencia:** el Durbin-Watson (tabla Resumen del modelo, sección 10) es **1,929**, muy cerca
  de 2: no hay autocorrelación.

En resumen, solo la independencia se cumple con claridad, por lo que las inferencias deben leerse con
cautela.
""")

# ==========================================================================
elif seccion == "5. Coeficientes y ecuación":
    st.header("5. Coeficientes y ecuación")
    st.markdown("Con n = 100, X̄ = 20.178,843, Ȳ = 73,6848, Sxx = 79.142.486.769,1 y "
                "Sxy = 14.044.679,0:")
    formula("b = Sxy / Sxx = 0,000177 &nbsp;&nbsp;&nbsp; a = Ȳ − b·X̄ = 70,104")
    spss("t08_coeficientes", "Coeficientes (REGRESIÓN, IBM SPSS Statistics).")
    formula("Ŷ = 70,104 + 0,000177·X")
    st.markdown("En la fila (Constante) está a y en la fila del PIB per cápita está b. El error típico "
                "de la estimación es s<sub>yx</sub> = 5,666 años.", unsafe_allow_html=True)

# ==========================================================================
elif seccion == "6. Interpretación de a y b":
    st.header("6. Interpretación de a y b")
    st.markdown(
        """
- **Pendiente b = 0,000177:** por cada dólar adicional de PIB per cápita la esperanza de vida aumenta
  en promedio 0,000177 años, es decir, unos **1,77 años por cada 10.000 dólares**.
- **Intercepto a = 70,10:** sería la esperanza de vida de un país con PIB per cápita igual a cero. Está
  fuera del rango observado (de 417 a 137.782 dólares), así que no tiene interpretación práctica.
  Además muestra el problema de la recta: las zonas rojas viven en promedio unos 59 años, muy por
  debajo de los 70 que da la recta en ese extremo.
""")

# ==========================================================================
elif seccion == "7. Inferencias sobre A y B":
    st.header("7. Inferencias sobre A y B")
    st.markdown("α = 0,05, valor crítico z<sub>0,975</sub> = 1,96. Los valores salen de la tabla "
                "Coeficientes.", unsafe_allow_html=True)
    spss("t08_coeficientes", "Coeficientes (REGRESIÓN, IBM SPSS Statistics).")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Pendiente.** H<sub>0</sub>: B = 0 contra H<sub>1</sub>: B ≠ 0", unsafe_allow_html=True)
        formula("z = b / s<sub>b</sub> = 0,000177 / 0,0000201 = 8,81")
        st.markdown("|z| = 8,81 > 1,96 (Sig. < 0,001): se rechaza H<sub>0</sub>.", unsafe_allow_html=True)
    with c2:
        st.markdown("**Intercepto.** H<sub>0</sub>: A = 0 contra H<sub>1</sub>: A ≠ 0", unsafe_allow_html=True)
        formula("z = a / s<sub>a</sub> = 70,104 / 0,697 = 100,54")
        st.markdown("|z| = 100,54 > 1,96 (Sig. < 0,001): se rechaza H<sub>0</sub>.", unsafe_allow_html=True)
    st.markdown(
        """
**Intervalos al 95 %:** B: 0,000177 ± 1,96 × 0,0000201 → (0,000138; 0,000217) y
A: 70,104 ± 1,96 × 0,697 → (68,737; 71,471). Cada 10.000 dólares se asocian con entre 1,38 y 2,17 años
más de vida. Los límites de SPSS difieren solo en la tercera cifra decimal porque usa 98 grados de
libertad.
""")

# ==========================================================================
elif seccion == "8. Intervalos y predicción":
    st.header("8. Intervalo para μy|x y para un valor particular Ya")
    st.markdown("Venezuela: X<sub>0</sub> = 4.244,5 dólares.", unsafe_allow_html=True)
    formula("Ŷ<sub>0</sub> = 70,104 + 0,000177 × 4.244,5 = 70,86 años")
    formula("S<sub>Ŷ0</sub> = 0,651 &nbsp;&nbsp;&nbsp; S<sub>Ya</sub> = 5,703")
    st.markdown(
        """
- **Media μy|x0:** 70,86 ± 1,96 × 0,651 → **(69,58; 72,13) años**.
- **Valor particular Ya:** 70,86 ± 1,96 × 5,703 → **(59,68; 82,04) años**.

El valor observado de Venezuela, 72,67 años, cae dentro del intervalo y está 1,81 años por encima del
pronóstico.
""")
    spss("t10_intervalos", "Pronósticos e intervalos al 95 % que guarda REGRESIÓN (IBM SPSS Statistics).")
    st.markdown("El intervalo de predicción es de unos ±11 años y crece lejos de X̄: para Estados Unidos "
                "pasa de 97 años, y Nigeria queda por debajo del suyo. La recta no describe bien los "
                "extremos.")

# ==========================================================================
elif seccion == "9. Inferencias sobre ρ":
    st.header("9. Inferencias sobre el coeficiente de correlación poblacional")
    spss("t05_correlaciones", "Correlación de Pearson (CORRELACIONES, IBM SPSS Statistics).")
    st.markdown("r = 0,665: correlación positiva y moderada. H<sub>0</sub>: ρ = 0 contra "
                "H<sub>1</sub>: ρ ≠ 0.", unsafe_allow_html=True)
    formula("z = r·√(n − 2) / √(1 − r²) = 0,6648 × √98 / √(1 − 0,4420) = 8,81")
    st.markdown(
        """
|z| = 8,81 > 1,96 (Sig. < 0,001): se rechaza H₀, hay correlación lineal en la población.
Esto no contradice el punto 4: hay una tendencia lineal significativa, pero la relación es curva,
por eso r es solo moderado.

**Intervalo con la transformación de Fisher:** z<sub>r</sub> = ½·ln(1,6648/0,3352) = 0,8014, error
estándar 1/√97 = 0,1015, intervalo 0,8014 ± 1,96 × 0,1015 = (0,6024; 1,0004). En la escala de r:
**IC 95 % para ρ = (0,539; 0,762)**, el mismo que da SPSS:
""", unsafe_allow_html=True)
    spss("t05b_ic_correlacion", "Intervalo de confianza para ρ con la transformación z de Fisher (IBM SPSS Statistics).")

# ==========================================================================
elif seccion == "10. Coeficiente de determinación":
    st.header("10. Coeficiente de determinación")
    spss("t06_resumen", "Resumen del modelo (REGRESIÓN, IBM SPSS Statistics).")
    formula("r² = SCReg / SCT = 2.492,378 / 5.638,653 = 0,442")
    st.markdown(
        """
El **44,2 %** de la variación de la esperanza de vida se explica por el PIB per cápita. El 55,8 %
restante depende de otros factores (salud, educación, conflictos, enfermedades) y de la forma curva de
la relación, que la recta no recoge. El r cuadrado ajustado es 0,436 y el error típico de la estimación
5,666 años.
""")

# ==========================================================================
elif seccion == "11. Análisis de varianza":
    st.header("11. Análisis de varianza (ANOVA)")
    spss("t07_anova", "ANOVA (REGRESIÓN, IBM SPSS Statistics).")
    st.markdown(
        """
H₀: B = 0 contra H₁: B ≠ 0, con valor crítico F(0,05; 1; 98) = 3,94.

- F = 77,632 > 3,94 (Sig. < 0,001): **el modelo es significativo**.
- SCT = SCReg + SCRes: 5.638,653 = 2.492,378 + 3.146,274.
- F = z² de la pendiente: 8,811² = 77,63.
- CME = 32,105 estima la varianza de los errores; su raíz es s<sub>yx</sub> = 5,666 años.
""", unsafe_allow_html=True)

# ==========================================================================
else:
    st.header("Conclusiones")
    st.markdown(
        """
1. **Hay relación positiva y significativa** entre el PIB per cápita y la esperanza de vida: las
   pruebas sobre B, sobre ρ y la F del ANOVA dan Sig. < 0,001. Recta: Ŷ = 70,104 + 0,000177·X
   (unos 1,77 años más por cada 10.000 dólares).
2. **La relación es moderada:** r = 0,665 y r² = 0,442.
3. **Los supuestos no se cumplen bien.** El ingreso tiene rendimientos decrecientes, así que fallan
   la linealidad y la normalidad y la homocedasticidad es dudosa; solo la independencia se cumple
   (Durbin-Watson = 1,929). La recta falla en los extremos: a Suiza le da más de 89 años y vive 84,4.
4. **Venezuela** vive 72,67 años, un poco más de lo esperado (70,86), y dentro de su intervalo de
   predicción. Las zonas azules (salvo Estados Unidos) viven más de lo que predice su ingreso y las
   zonas rojas mucho menos.
5. **Recomendaciones:** agregar otras variables (gasto en salud, escolaridad), comparar varios años y
   tratar con cuidado los datos de Venezuela.
""")
    st.subheader("Fuente de los datos")
    st.markdown(
        """
Banco Mundial, *Indicadores del Desarrollo Mundial*. Datos descargados el 15/11/2026.

- **NY.GDP.PCAP.CD**: PIB per cápita (US$ a precios actuales), 2024.
- **SP.DYN.LE00.IN**: esperanza de vida al nacer, total (años), 2024.

Procesamiento, tablas y gráficos en IBM SPSS Statistics (sintaxis en `spss/regresion_v6.sps`). El mapa
de la sección 1 se hizo con Plotly.
""")

st.markdown(
    "<div class='pie-pagina'>Estadística II · Escuela de Estadística y Ciencias Actuariales, UCV · "
    "Allan Arcia y Eddie Palomino · Profesoras Sandra Pinto y Yuraisi Capriles · "
    "Fuente: Banco Mundial, Indicadores del Desarrollo Mundial (2024)</div>",
    unsafe_allow_html=True)
