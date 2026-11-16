"""Regresión lineal bivariante: PIB per cápita y esperanza de vida (2024).

Trabajo de Estadística II - UCV, Escuela de Estadística y Ciencias Actuariales.
Ejecutar desde la raíz del proyecto:  streamlit run app.py

Todos los resultados numéricos salen de src/regresion.py (el mismo módulo que
usa el informe en Word), así que la app y el informe coinciden.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from scipy import stats

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))
import regresion as rg  # noqa: E402

RUTA_CSV = RAIZ / "data" / "pib_esperanza_vida_2024.csv"

st.set_page_config(
    page_title="PIB per cápita y esperanza de vida · Estadística II",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Paleta y constantes
# --------------------------------------------------------------------------
TINTA = "#1d2733"
TINTA_2 = "#5b6673"
AZUL_UCV = "#1f4e79"
REJILLA = "#e4e1da"
COLOR_GRUPO = {
    "Otro": "#a3abb5",
    "Zona azul": "#2a78d6",
    "Zona roja": "#eb6834",
    "Venezuela": "#1baf7a",
}
ORDEN_GRUPO = ["Otro", "Zona roja", "Zona azul", "Venezuela"]
ORDEN_INGRESO = ["Ingreso bajo", "Ingreso mediano bajo", "Ingreso mediano alto", "Ingreso alto"]
X, Y = "pib_pc_usd_2024", "esperanza_vida_2024"
TICKS_PIB = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]

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


# --------------------------------------------------------------------------
# Formato de números en español
# --------------------------------------------------------------------------
def num(x, d=2):
    """1234.5 -> '1.234,50' (coma decimal, punto de miles)."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pval(p):
    if p is None or np.isnan(p):
        return "—"
    if p >= 0.0001:
        return num(p, 4)
    mant, exp = f"{p:.1e}".split("e")
    sup = str(int(exp)).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{mant.replace('.', ',')}\u00a0×\u00a010{sup}"


def ltx(x, d=2):
    """Número con coma decimal para usar dentro de LaTeX."""
    return num(x, d).replace(",", "{,}")


def ltx_p(p):
    if p >= 0.0001:
        return ltx(p, 4)
    mant, exp = f"{p:.1e}".split("e")
    return f"{mant.replace('.', '{,}')}\\times 10^{{{int(exp)}}}"


def ic(par, d=2):
    return f"({num(par[0], d)}; {num(par[1], d)})"


# --------------------------------------------------------------------------
# Datos y modelos (una sola vez)
# --------------------------------------------------------------------------
@st.cache_resource
def preparar():
    df = rg.cargar_datos(str(RUTA_CSV))
    lin, log = rg.modelos(df)
    df = df.copy()
    df["ajustado_m1"], df["residuo_m1"] = lin.res["yhat"], lin.res["e"]
    df["ajustado_m2"], df["residuo_m2"] = log.res["yhat"], log.res["e"]
    return df, lin, log, lin.supuestos(), log.supuestos()


df, LIN, LOG, SUP_LIN, SUP_LOG = preparar()
R1, R2 = LIN.res, LOG.res
VEN = df.loc[df["grupo"] == "Venezuela"].iloc[0]


def intervalos_nivel(m, pib, nivel=0.95):
    """Ŷ e intervalos al nivel pedido. Al 95 % se devuelve tal cual lo que da
    el módulo; para otro nivel se usan sus mismos errores estándar con el t
    de Student de gl = n - 2."""
    iv = m.intervalos(pib)
    if abs(nivel - 0.95) < 1e-9:
        return iv["y0"], iv["ic_media"], iv["ic_pred"], m.res["tcrit"], iv
    t = stats.t.ppf(1 - (1 - nivel) / 2, m.res["gl"])
    y0 = iv["y0"]
    return (y0, (y0 - t * iv["se_media"], y0 + t * iv["se_media"]),
            (y0 - t * iv["se_pred"], y0 + t * iv["se_pred"]), t, iv)


# --------------------------------------------------------------------------
# Estilos
# --------------------------------------------------------------------------
st.markdown(
    """
<style>
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px;}
h1, h2, h3 {font-family: Georgia, 'Times New Roman', serif; color: #16324f; letter-spacing: -0.01em;}
h2 {border-bottom: 2px solid #d9d3c5; padding-bottom: .35rem;}
[data-testid="stSidebar"] {border-right: 1px solid #ddd8cc;}
[data-testid="stSidebar"] .stRadio label p {font-size: .95rem;}

.portada {background: linear-gradient(135deg, #16324f 0%, #1f4e79 60%, #2f6aa3 100%);
  color: #fff; border-radius: 14px; padding: 2.2rem 2.6rem 2rem; margin-bottom: 1.2rem;
  box-shadow: 0 8px 24px rgba(22,50,79,.18);}
.portada .inst {font-size: .82rem; letter-spacing: .14em; text-transform: uppercase; opacity: .85;}
.portada h1 {color: #fff; font-size: 2.35rem; line-height: 1.15; margin: .7rem 0 .5rem; padding: 0;}
.portada .sub {font-size: 1.1rem; opacity: .92; max-width: 60rem;}
.portada .pie {display: flex; gap: 2.2rem; flex-wrap: wrap; margin-top: 1.5rem; padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,.28); font-size: .95rem;}
.portada .pie b {display: block; font-size: .72rem; letter-spacing: .12em; text-transform: uppercase;
  opacity: .75; font-weight: 600; margin-bottom: .15rem;}

.fila {display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .8rem; margin: .4rem 0 1.1rem;}
.tarjeta {background: #fff; border: 1px solid #e1dccf; border-left: 4px solid #1f4e79; border-radius: 10px;
  padding: .8rem 1rem .75rem; box-shadow: 0 1px 3px rgba(0,0,0,.04);}
.tarjeta .et {font-size: .74rem; letter-spacing: .08em; text-transform: uppercase; color: #5b6673; font-weight: 600;}
.tarjeta .va {font-family: Georgia, serif; font-size: 1.75rem; color: #16324f; line-height: 1.2; margin-top: .15rem;
  font-variant-numeric: tabular-nums;}
.tarjeta .no {font-size: .8rem; color: #5b6673; margin-top: .1rem;}
.tarjeta.verde {border-left-color: #1baf7a;} .tarjeta.naranja {border-left-color: #eb6834;}
.tarjeta.gris {border-left-color: #a3abb5;}

.caja {background: #fff; border: 1px solid #e1dccf; border-radius: 10px; padding: 1rem 1.2rem; margin: .5rem 0 1rem;}
.caja.clave {border-left: 4px solid #1baf7a;}
.caja.aviso {border-left: 4px solid #eb6834;}
.caja p:last-child {margin-bottom: 0;}

table.tabla {border-collapse: collapse; width: 100%; background: #fff; font-size: .93rem;
  border: 1px solid #e1dccf; border-radius: 10px; overflow: hidden; margin: .3rem 0 1rem;}
table.tabla th {background: #16324f; color: #fff; text-align: right; padding: .5rem .7rem; font-weight: 600;
  font-size: .82rem; letter-spacing: .02em;}
table.tabla td {padding: .42rem .7rem; text-align: right; border-top: 1px solid #ece8de;
  font-variant-numeric: tabular-nums;}
table.tabla th:first-child, table.tabla td:first-child {text-align: left;}
table.tabla tr:nth-child(even) td {background: #faf8f3;}
table.tabla.texto3 th:nth-child(-n+3), table.tabla.texto3 td:nth-child(-n+3) {text-align: left;}
.ok, .no_ok {display: inline-block; padding: .08rem .55rem; border-radius: 999px; font-size: .8rem; font-weight: 600; white-space: nowrap;}
.ok {background: #e3f4ec; color: #0d6b49;} .no_ok {background: #fdebe2; color: #a8431a;}
.pie-pagina {color: #5b6673; font-size: .82rem; border-top: 1px solid #ddd8cc; margin-top: 2.5rem; padding-top: .8rem;}
.leyenda span {display: inline-flex; align-items: center; margin-right: 1.1rem; font-size: .9rem; color: #1d2733;}
.leyenda i {width: 11px; height: 11px; border-radius: 50%; display: inline-block; margin-right: .4rem;}
</style>
""",
    unsafe_allow_html=True,
)


def tarjetas(items):
    """items: lista de (etiqueta, valor, nota[, clase])."""
    html = '<div class="fila">'
    for it in items:
        et, va, no = it[:3]
        cl = it[3] if len(it) > 3 else ""
        html += (f'<div class="tarjeta {cl}"><div class="et">{et}</div>'
                 f'<div class="va">{va}</div><div class="no">{no}</div></div>')
    st.markdown(html + "</div>", unsafe_allow_html=True)


def tabla(d: pd.DataFrame, clase=""):
    st.markdown(d.to_html(index=False, escape=False, classes=f"tabla {clase}".strip(), border=0),
                unsafe_allow_html=True)


def caja(texto, clase=""):
    st.markdown(f'<div class="caja {clase}">{texto}</div>', unsafe_allow_html=True)


def insignia(cumple, si="No se rechaza H₀", no="Se rechaza H₀"):
    return f'<span class="ok">{si}</span>' if cumple else f'<span class="no_ok">{no}</span>'


# --------------------------------------------------------------------------
# Gráficos
# --------------------------------------------------------------------------
def estilo(fig, alto=460, leyenda=True):
    fig.update_layout(
        height=alto, separators=",.", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff",
        font=dict(family="Source Sans Pro, Segoe UI, Helvetica, Arial, sans-serif", size=14, color=TINTA),
        margin=dict(l=66, r=18, t=44 if fig.layout.title.text else 16, b=58),
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#c9c3b5", font=dict(color=TINTA, size=13)),
    )
    fig.update_xaxes(gridcolor=REJILLA, linecolor="#b9b3a5", zeroline=False, ticks="outside",
                     tickcolor="#b9b3a5", title_font=dict(color=TINTA_2, size=13), title_standoff=10,
                     automargin=False)
    fig.update_yaxes(gridcolor=REJILLA, linecolor="#b9b3a5", zeroline=False,
                     title_font=dict(color=TINTA_2, size=13), title_standoff=10, automargin=False)
    return fig


def mostrar(fig, clave):
    st.plotly_chart(fig, width="stretch", theme=None, key=clave,
                    config={"displaylogo": False, "locale": "es",
                            "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]})


def eje_pib_log(fig, **kw):
    fig.update_xaxes(type="log", tickvals=TICKS_PIB, ticktext=[num(v, 0) for v in TICKS_PIB],
                     tickangle=0,
                     title_text="PIB per cápita (US$ corrientes, escala logarítmica)", **kw)


def fig_dispersion(m, eje_log, conf=True, pred=True, nivel=0.95, etiquetar=False, alto=540, leyenda=True):
    """Dispersión con recta ajustada y bandas. El eje X siempre es el PIB en US$."""
    lo, hi = df[X].min() * 0.85, df[X].max() * 1.12
    malla = np.geomspace(lo, hi, 240) if (m.log or eje_log) else np.linspace(lo, hi, 240)
    iv = m.intervalos(malla)
    t = m.res["tcrit"] if abs(nivel - 0.95) < 1e-9 else stats.t.ppf(1 - (1 - nivel) / 2, m.res["gl"])
    y0 = iv["y0"]
    pct = f"{int(round(nivel * 100))} %"
    fig = go.Figure()
    if pred:
        fig.add_trace(go.Scatter(x=malla, y=y0 + t * iv["se_pred"], mode="lines", line=dict(width=0),
                                 hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=malla, y=y0 - t * iv["se_pred"], mode="lines", line=dict(width=0),
                                 fill="tonexty", fillcolor="rgba(31,78,121,0.09)", hoverinfo="skip",
                                 name=f"Intervalo de predicción {pct}"))
    if conf:
        fig.add_trace(go.Scatter(x=malla, y=y0 + t * iv["se_media"], mode="lines", line=dict(width=0),
                                 hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=malla, y=y0 - t * iv["se_media"], mode="lines", line=dict(width=0),
                                 fill="tonexty", fillcolor="rgba(31,78,121,0.28)", hoverinfo="skip",
                                 name=f"Intervalo de confianza {pct} (media)"))
    fig.add_trace(go.Scatter(x=malla, y=y0, mode="lines", line=dict(color="#16324f", width=2.5),
                             name="Recta ajustada" if (not m.log or eje_log) else "Curva ajustada",
                             hovertemplate="PIB: US$ %{x:,.0f}<br>Ŷ = %{y:,.2f} años<extra></extra>"))
    for g in ORDEN_GRUPO:
        d = df[df["grupo"] == g]
        ven = g == "Venezuela"
        con_texto = etiquetar and (g == "Zona azul" or (g == "Zona roja" and eje_log))
        fig.add_trace(go.Scatter(
            x=d[X], y=d[Y], mode="markers+text" if con_texto else "markers",
            name={"Otro": "Otros países"}.get(g, g),
            text=d["pais"] if con_texto else None, textposition="top center",
            textfont=dict(size=11, color=TINTA_2),
            marker=dict(color=COLOR_GRUPO[g], size=15 if ven else (10 if g != "Otro" else 8.5),
                        symbol="star" if ven else "circle",
                        opacity=0.8 if g == "Otro" else 1, line=dict(color="#ffffff", width=1.2)),
            customdata=np.stack([d["pais"], d["ingreso"]], axis=1),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>PIB per cápita: US$ %{x:,.1f}"
                          "<br>Esperanza de vida: %{y:,.2f} años<extra></extra>"))
    xv = np.log10(VEN[X]) if eje_log else VEN[X]
    fig.add_annotation(x=xv, y=VEN[Y], text="<b>Venezuela</b>", showarrow=True, arrowhead=0, arrowwidth=1.2,
                       arrowcolor=TINTA_2, ax=-55 if eje_log else 70, ay=-42 if eje_log else 45, font=dict(size=13, color=TINTA),
                       bgcolor="rgba(255,255,255,0.85)", borderpad=2)
    estilo(fig, alto, leyenda=leyenda)
    if eje_log:
        eje_pib_log(fig, range=[np.log10(lo), np.log10(hi)])
    else:
        fig.update_xaxes(title_text="PIB per cápita (US$ corrientes)", tickformat=",.0f", range=[-2500, hi])
    fig.update_yaxes(title_text="Esperanza de vida al nacer (años)", range=[50, 92])
    return fig


def fig_residuos(m, col_aj, col_res):
    e, s = m.res["e"], m.res["s"]
    c1, c2, c3 = st.columns(3)
    # residuos vs ajustados
    f = go.Figure()
    f.add_hline(y=0, line=dict(color=TINTA_2, width=1.2, dash="dash"))
    for g in ORDEN_GRUPO:
        d = df[df["grupo"] == g]
        f.add_trace(go.Scatter(x=d[col_aj], y=d[col_res], mode="markers", name=g,
                               marker=dict(color=COLOR_GRUPO[g], size=8.5, line=dict(color="#fff", width=1),
                                           opacity=0.85 if g == "Otro" else 1),
                               customdata=d["pais"],
                               hovertemplate="<b>%{customdata}</b><br>Ajustado: %{x:,.2f}<br>Residuo: %{y:,.2f}<extra></extra>"))
    estilo(f, 360, leyenda=False)
    f.update_layout(title=dict(text="Residuos vs. valores ajustados", font=dict(size=15)), margin_t=48)
    f.update_xaxes(title_text="Valor ajustado Ŷ (años)")
    f.update_yaxes(title_text="Residuo e (años)")
    with c1:
        mostrar(f, f"rva_{m.log}")
    # QQ
    (teo, obs), (pend, orde, _) = stats.probplot(e, dist="norm")
    orden = np.argsort(e)
    f = go.Figure()
    f.add_trace(go.Scatter(x=[teo.min(), teo.max()], y=[orde + pend * teo.min(), orde + pend * teo.max()],
                           mode="lines", line=dict(color="#16324f", width=2), hoverinfo="skip"))
    f.add_trace(go.Scatter(x=teo, y=obs, mode="markers",
                           marker=dict(color="#4d7fb0", size=8, line=dict(color="#fff", width=1)),
                           customdata=df["pais"].to_numpy()[orden],
                           hovertemplate="<b>%{customdata}</b><br>Cuantil teórico: %{x:,.2f}<br>Residuo: %{y:,.2f}<extra></extra>"))
    estilo(f, 360, leyenda=False)
    f.update_layout(title=dict(text="Gráfico Q-Q normal de los residuos", font=dict(size=15)), margin_t=48)
    f.update_xaxes(title_text="Cuantil teórico N(0, 1)")
    f.update_yaxes(title_text="Residuo ordenado (años)")
    with c2:
        mostrar(f, f"qq_{m.log}")
    # histograma
    f = go.Figure()
    ancho = 2.0
    ini = np.floor(e.min() / ancho) * ancho
    f.add_trace(go.Histogram(x=e, xbins=dict(start=ini, end=e.max() + ancho, size=ancho),
                             marker=dict(color="#4d7fb0", line=dict(color="#fff", width=1.5)),
                             hovertemplate="Residuo: %{x}<br>Países: %{y}<extra></extra>"))
    xs = np.linspace(e.min() - 2, e.max() + 2, 200)
    f.add_trace(go.Scatter(x=xs, y=stats.norm.pdf(xs, 0, s) * len(e) * ancho, mode="lines",
                           line=dict(color="#16324f", width=2), hoverinfo="skip"))
    estilo(f, 360, leyenda=False)
    f.update_layout(title=dict(text="Histograma de residuos y curva normal", font=dict(size=15)), margin_t=48, bargap=0)
    f.update_xaxes(title_text="Residuo e (años)")
    f.update_yaxes(title_text="Número de países")
    with c3:
        mostrar(f, f"hist_{m.log}")


def titulo(texto, bajada=None):
    st.header(texto)
    if bajada:
        st.markdown(f"<p style='color:{TINTA_2};font-size:1.05rem;margin:.1rem 0 1rem'>{bajada}</p>",
                    unsafe_allow_html=True)


LEYENDA_GRUPOS = (
    '<div class="leyenda">'
    + "".join(f'<span><i style="background:{COLOR_GRUPO[g]}"></i>{t}</span>' for g, t in [
        ("Venezuela", "Venezuela"), ("Zona azul", "Zona azul"), ("Zona roja", "Zona roja"), ("Otro", "Otros países")])
    + "</div>")

# --------------------------------------------------------------------------
# Barra lateral
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Estadística II")
    st.caption("Regresión lineal bivariante · UCV")
    seccion = st.radio("Contenido", SECCIONES, label_visibility="collapsed")
    st.divider()
    st.markdown(
        f"**Modelo principal**  \nŶ = {num(R2['a'], 4)} + {num(R2['b'], 4)} · ln(PIB)  \n"
        f"r = {num(R2['r'], 4)} · R² = {num(R2['r2'], 4)}")
    st.caption("Allan Arcia y Eddie Palomino  \nProfesoras: Sandra Pinto y Yuraisi Capriles")

# ==========================================================================
# PORTADA
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
    tarjetas([
        ("Países (n)", f"{R2['n']}", "muestra de 2024", "gris"),
        ("Correlación r", num(R2["r"], 4), "entre ln(PIB) y esperanza de vida"),
        ("R²", num(R2["r2"], 4), f"{num(100 * R2['r2'], 1)} % de la variación explicada"),
        ("Pendiente b", num(R2["b"], 4), "años por unidad de ln(PIB)"),
        ("F de Fisher", num(R2["F"], 2), f"p = {pval(R2['p_F'])}"),
    ])
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        mostrar(fig_dispersion(LOG, True, conf=True, pred=False, alto=450, leyenda=False), "portada")
        st.markdown(LEYENDA_GRUPOS, unsafe_allow_html=True)
        st.caption("Recta ajustada del modelo 2 con su banda de confianza del 95 % para la media.")
    with c2:
        st.subheader("El trabajo en pocas líneas")
        st.markdown(
            f"""
- **X:** PIB per cápita en US$ corrientes (2024). **Y:** esperanza de vida al nacer en años (2024).
- La relación no es una recta en la escala original: los primeros dólares «compran» muchos más años
  de vida que los últimos. Por eso el modelo principal usa **ln(PIB)**.
- Ecuación estimada: **Ŷ = {num(R2['a'], 4)} + {num(R2['b'], 4)} · ln(PIB)**.
- Duplicar el PIB per cápita se asocia con unos **{num(R2['b'] * np.log(2), 2)} años** más de
  esperanza de vida.
- **Venezuela** (US$ {num(VEN[X], 1)}) vive {num(VEN[Y], 2)} años; el modelo esperaba
  {num(float(LOG.intervalos(VEN[X])['y0']), 2)}.
""")
        st.caption("Use el índice de la izquierda para recorrer las secciones en el orden del guion.")

# ==========================================================================
# 1. DATOS
# ==========================================================================
elif seccion == "1. Datos":
    titulo("1. Datos", "100 países con ambos indicadores disponibles para 2024 en el Banco Mundial.")
    tarjetas([
        ("Países", f"{len(df)}", f"{df['region'].nunique()} regiones del Banco Mundial", "gris"),
        ("Variable X", "PIB per cápita", "US$ corrientes · NY.GDP.PCAP.CD"),
        ("Variable Y", "Esperanza de vida", "años al nacer · SP.DYN.LE00.IN"),
        ("Venezuela", f"US$ {num(VEN[X], 1)}", f"{num(VEN[Y], 2)} años de esperanza de vida", "verde"),
    ])
    st.markdown(
        "Además de Venezuela, se destacan dos grupos de comparación: los países que albergan las llamadas "
        "**zonas azules** de longevidad (Japón, Italia, Grecia, Costa Rica y Estados Unidos) y un grupo de "
        "**zona roja** formado por diez países de África Subsahariana con esperanzas de vida muy bajas.")

    st.subheader("Mapa de la muestra")
    opcion = st.radio("Variable del mapa", ["PIB per cápita", "Esperanza de vida", "Residuo del modelo 2"],
                      horizontal=True)
    base = dict(locations=df["iso3"], locationmode="ISO-3", marker_line_color="#ffffff", marker_line_width=0.6)
    if opcion == "PIB per cápita":
        tv = [500, 2000, 10000, 50000]
        traza = go.Choropleth(
            z=np.log10(df[X]), colorscale=[[0, "#dbe8f5"], [0.5, "#5b94c9"], [1, "#12365a"]],
            customdata=np.stack([df["pais"], df[X]], axis=1),
            hovertemplate="<b>%{customdata[0]}</b><br>PIB per cápita: US$ %{customdata[1]:,.1f}<extra></extra>",
            colorbar=dict(title="US$", tickvals=np.log10(tv), ticktext=[num(v, 0) for v in tv]), **base)
        nota = "Color en escala logarítmica: de claro (menor ingreso) a oscuro (mayor ingreso)."
    elif opcion == "Esperanza de vida":
        traza = go.Choropleth(
            z=df[Y], colorscale=[[0, "#dbe8f5"], [0.5, "#5b94c9"], [1, "#12365a"]],
            customdata=np.stack([df["pais"], df[Y]], axis=1),
            hovertemplate="<b>%{customdata[0]}</b><br>Esperanza de vida: %{customdata[1]:,.2f} años<extra></extra>",
            colorbar=dict(title="Años"), **base)
        nota = "De claro (menor esperanza de vida) a oscuro (mayor esperanza de vida)."
    else:
        lim = float(np.abs(df["residuo_m2"]).max())
        traza = go.Choropleth(
            z=df["residuo_m2"], zmin=-lim, zmax=lim, zmid=0,
            colorscale=[[0, "#c9501f"], [0.5, "#e9e9e6"], [1, "#1f63b5"]],
            customdata=np.stack([df["pais"], df["residuo_m2"], df[Y], df["ajustado_m2"]], axis=1),
            hovertemplate="<b>%{customdata[0]}</b><br>Observada: %{customdata[2]:,.2f} años"
                          "<br>Esperada por el modelo: %{customdata[3]:,.2f} años"
                          "<br>Residuo: %{customdata[1]:+,.2f} años<extra></extra>",
            colorbar=dict(title="Años"), **base)
        nota = ("Residuo = esperanza de vida observada − esperada según su PIB. Azul: el país vive más de lo "
                "que predice su ingreso; naranja: vive menos.")
    mapa = go.Figure(traza)
    mapa.update_geos(projection_type="natural earth", showframe=False, showcoastlines=False,
                     showland=True, landcolor="#efece5", showcountries=True, countrycolor="#ffffff",
                     bgcolor="rgba(0,0,0,0)", lataxis_range=[-58, 85])
    mapa.update_layout(height=500, margin=dict(l=0, r=0, t=0, b=0), separators=",.",
                       paper_bgcolor="rgba(0,0,0,0)", font=dict(color=TINTA, size=13),
                       hoverlabel=dict(bgcolor="#fff", font=dict(color=TINTA)))
    mapa.update_traces(colorbar=dict(len=0.7, thickness=14, outlinewidth=0))
    mostrar(mapa, "mapa")
    st.caption(nota + " Los países en gris claro no forman parte de la muestra.")

    st.subheader("Tabla de datos")
    f1, f2, f3, f4 = st.columns([2, 2, 2, 2])
    busca = f1.text_input("Buscar país", placeholder="Ej.: Venezuela")
    regiones = f2.multiselect("Región", sorted(df["region"].unique()), placeholder="Todas")
    ingresos = f3.multiselect("Grupo de ingreso", ORDEN_INGRESO, placeholder="Todos")
    grupos = f4.multiselect("Grupo de comparación", ["Venezuela", "Zona azul", "Zona roja", "Otro"],
                            placeholder="Todos")
    v = df
    if busca:
        v = v[v["pais"].str.contains(busca.strip(), case=False, regex=False)
              | v["iso3"].str.contains(busca.strip(), case=False, regex=False)]
    if regiones:
        v = v[v["region"].isin(regiones)]
    if ingresos:
        v = v[v["ingreso"].isin(ingresos)]
    if grupos:
        v = v[v["grupo"].isin(grupos)]
    v = v[["iso3", "pais", "region", "ingreso", "grupo", X, "ln_pib_pc", Y, "ajustado_m2", "residuo_m2"]].rename(
        columns={"iso3": "ISO3", "pais": "País", "region": "Región", "ingreso": "Ingreso", "grupo": "Grupo",
                 X: "PIB per cápita (US$)", "ln_pib_pc": "ln(PIB)", Y: "Esperanza de vida (años)",
                 "ajustado_m2": "Ŷ modelo 2", "residuo_m2": "Residuo modelo 2"})
    es = dict(decimal=",", thousands=".")
    st.dataframe(
        v.style.format({"PIB per cápita (US$)": "{:,.1f}", "ln(PIB)": "{:.4f}", "Esperanza de vida (años)": "{:.3f}",
                        "Ŷ modelo 2": "{:.2f}", "Residuo modelo 2": "{:+.2f}"}, **es),
        width="stretch", height=390, hide_index=True)
    c1, c2 = st.columns([3, 1])
    c1.caption(f"Se muestran {len(v)} de {len(df)} países. Se puede ordenar haciendo clic en cada encabezado.")
    c2.download_button("Descargar CSV original", RUTA_CSV.read_bytes(), "pib_esperanza_vida_2024.csv",
                       "text/csv", width="stretch")

# ==========================================================================
# 2. DESCRIPTIVAS
# ==========================================================================
elif seccion == "2. Estadísticas descriptivas":
    titulo("2. Estadísticas descriptivas", "Cómo se distribuye cada variable antes de relacionarlas.")
    variables = {"PIB per cápita (US$)": X, "ln(PIB per cápita)": "ln_pib_pc", "Esperanza de vida (años)": Y}
    desc = {k: rg.descriptivas(df[c]) for k, c in variables.items()}
    dec = {"PIB per cápita (US$)": 1, "ln(PIB per cápita)": 4, "Esperanza de vida (años)": 3}
    filas = []
    for medida in next(iter(desc.values())):
        fila = {"Medida": medida}
        for k in variables:
            val = desc[k][medida]
            if medida == "n":
                fila[k] = f"{int(val)}"
            elif medida in ("Coef. de variación (%)", "Asimetría", "Curtosis (exceso)"):
                fila[k] = num(val, 2)
            elif medida == "Varianza" and k == "PIB per cápita (US$)":
                fila[k] = num(val, 0)
            else:
                fila[k] = num(val, dec[k])
        filas.append(fila)
    d_pib, d_ev = desc["PIB per cápita (US$)"], desc["Esperanza de vida (años)"]

    c1, c2 = st.columns([5, 6], gap="large")
    with c1:
        tabla(pd.DataFrame(filas))
    with c2:
        elegida = st.radio("Variable", list(variables), horizontal=True)
        col = variables[elegida]
        f = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.2, 0.8], vertical_spacing=0.04)
        f.add_trace(go.Box(x=df[col], orientation="h", marker=dict(color=AZUL_UCV, size=5), line=dict(width=1.6),
                           fillcolor="rgba(31,78,121,0.18)", boxpoints="outliers", name="", text=df["pais"],
                           hovertemplate="%{text}: %{x:,.2f}<extra></extra>"), row=1, col=1)
        f.add_trace(go.Histogram(x=df[col], nbinsx=18,
                                 marker=dict(color="#4d7fb0", line=dict(color="#fff", width=1.5)),
                                 hovertemplate="Intervalo: %{x}<br>Países: %{y}<extra></extra>"), row=2, col=1)
        med_der = desc[elegida]["Media"] >= desc[elegida]["Mediana"]
        f.add_vline(x=desc[elegida]["Media"], line=dict(color="#16324f", width=1.5, dash="dash"), row=2, col=1,
                    annotation_text=f"Media {num(desc[elegida]['Media'], dec[elegida] if col != X else 0)}",
                    annotation_position="top right" if med_der else "top left",
                    annotation_font=dict(size=12, color=TINTA))
        f.add_vline(x=desc[elegida]["Mediana"], line=dict(color="#eb6834", width=1.5, dash="dot"), row=2, col=1,
                    annotation_text=f"Mediana {num(desc[elegida]['Mediana'], dec[elegida] if col != X else 0)}",
                    annotation_position="top left" if med_der else "top right",
                    annotation_font=dict(size=12, color=TINTA))
        estilo(f, 470, leyenda=False)
        f.update_layout(bargap=0)
        f.update_yaxes(showticklabels=False, showgrid=False, row=1, col=1)
        f.update_xaxes(ticks="", row=1, col=1)
        f.update_yaxes(title_text="Número de países", row=2, col=1)
        f.update_xaxes(title_text=elegida, tickformat=",.0f" if col == X else None, row=2, col=1)
        mostrar(f, "hist_desc")

    caja(
        f"<p><b>Lectura.</b> El PIB per cápita es muy asimétrico a la derecha (asimetría {num(d_pib['Asimetría'], 2)}): "
        f"la media (US$ {num(d_pib['Media'], 0)}) casi triplica a la mediana (US$ {num(d_pib['Mediana'], 0)}) y su "
        f"coeficiente de variación es de {num(d_pib['Coef. de variación (%)'], 0)} %. Al tomar logaritmo la distribución "
        f"queda prácticamente simétrica (asimetría {num(desc['ln(PIB per cápita)']['Asimetría'], 2)}). "
        f"La esperanza de vida es mucho más homogénea: media de {num(d_ev['Media'], 2)} años, desviación estándar de "
        f"{num(d_ev['Desviación estándar'], 2)} años y un rango que va de {num(d_ev['Mínimo'], 1)} a "
        f"{num(d_ev['Máximo'], 1)} años.</p>", "clave")

    st.subheader("Comparación por grupos")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**Esperanza de vida según el grupo de ingreso del Banco Mundial**")
        f = go.Figure()
        for g in ORDEN_INGRESO:
            d = df[df["ingreso"] == g]
            f.add_trace(go.Box(y=d[Y], name=g.replace("Ingreso ", "").capitalize(), boxpoints="all", jitter=0.45,
                               pointpos=0, marker=dict(color=AZUL_UCV, size=5, opacity=0.55),
                               line=dict(color=AZUL_UCV, width=1.6), fillcolor="rgba(31,78,121,0.12)",
                               text=d["pais"], hovertemplate="<b>%{text}</b><br>%{y:,.2f} años<extra></extra>"))
        estilo(f, 400, leyenda=False)
        f.update_yaxes(title_text="Esperanza de vida (años)")
        f.update_xaxes(title_text="Grupo de ingreso")
        mostrar(f, "box_ingreso")
        res = []
        for g in ORDEN_INGRESO:
            d = df[df["ingreso"] == g]
            dx, dy = rg.descriptivas(d[X]), rg.descriptivas(d[Y])
            res.append({"Grupo de ingreso": g, "n": dx["n"], "PIB pc mediano (US$)": num(dx["Mediana"], 0),
                        "Esp. de vida media": num(dy["Media"], 2), "Desv. estándar": num(dy["Desviación estándar"], 2)})
        tabla(pd.DataFrame(res))
    with c2:
        st.markdown("**Venezuela frente a las zonas azules y rojas**")
        f = go.Figure()
        for g in ["Zona roja", "Otro", "Zona azul"]:
            d = df[df["grupo"] == g]
            f.add_trace(go.Box(y=d[Y], name={"Otro": "Otros países"}.get(g, g), boxpoints="all", jitter=0.45,
                               pointpos=0, marker=dict(color=COLOR_GRUPO[g], size=6, opacity=0.75),
                               line=dict(color=COLOR_GRUPO[g], width=1.8), text=d["pais"],
                               hovertemplate="<b>%{text}</b><br>%{y:,.2f} años<extra></extra>"))
        f.add_hline(y=VEN[Y], line=dict(color=COLOR_GRUPO["Venezuela"], width=2.5),
                    annotation_text=f"<b>Venezuela: {num(VEN[Y], 2)} años</b>", annotation_position="top left",
                    annotation_font=dict(color=TINTA, size=13))
        estilo(f, 400, leyenda=False)
        f.update_yaxes(title_text="Esperanza de vida (años)")
        mostrar(f, "box_grupo")
        res = []
        for g in ["Venezuela", "Zona azul", "Zona roja", "Otro"]:
            d = df[df["grupo"] == g]
            dx, dy = rg.descriptivas(d[X]), rg.descriptivas(d[Y])
            res.append({"Grupo": {"Otro": "Otros países"}.get(g, g), "n": dx["n"],
                        "PIB pc medio (US$)": num(dx["Media"], 0), "Esp. de vida media": num(dy["Media"], 2),
                        "Mínimo": num(dy["Mínimo"], 2), "Máximo": num(dy["Máximo"], 2)})
        tabla(pd.DataFrame(res))

# ==========================================================================
# 3. DISPERSIÓN
# ==========================================================================
elif seccion == "3. Diagrama de dispersión":
    titulo("3. Diagrama de dispersión", "La forma de la nube de puntos decide qué modelo tiene sentido.")
    c1, c2 = st.columns([5, 3])
    vista = c1.radio(
        "Modelo y escala",
        ["Modelo 1: Y sobre PIB", "Modelo 2: Y sobre ln(PIB)", "Modelo 2 en la escala original"],
        index=1, horizontal=True)
    with c2:
        st.markdown("<div style='font-size:.875rem;margin-bottom:.45rem'>Bandas al 95 % y etiquetas</div>",
                    unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        conf = k1.checkbox("Confianza", True)
        pred = k2.checkbox("Predicción", True)
        etiq = k3.checkbox("Etiquetas", False, help="Nombres de los países de las zonas azul y roja (la zona roja solo se etiqueta en la escala logarítmica, donde no se solapa).")
    m = LIN if vista.startswith("Modelo 1") else LOG
    r = m.res
    mostrar(fig_dispersion(m, vista == "Modelo 2: Y sobre ln(PIB)", conf, pred, etiquetar=etiq), "disp")
    ecu = (f"Ŷ = {num(r['a'], 4)} + {num(r['b'], 6)} · PIB" if not m.log
           else f"Ŷ = {num(r['a'], 4)} + {num(r['b'], 4)} · ln(PIB)")
    tarjetas([
        ("Ecuación ajustada", f"<span style='font-size:.98rem;white-space:nowrap'>{ecu}</span>", m.nombre, "gris"),
        ("r", num(r["r"], 4), "correlación lineal"),
        ("R²", num(r["r2"], 4), "variación explicada"),
        ("Error estándar s", num(r["s"], 3), "años"),
    ])
    if not m.log:
        caja("<p><b>Qué se ve.</b> La nube tiene forma de «L acostada»: entre los países pobres la esperanza de vida "
             "sube muy rápido con el ingreso y después se aplana. Una recta sobre el PIB en dólares pasa por debajo "
             "de los países de ingreso medio y sobreestima a los más pobres; la relación es directa, pero "
             "<b>no es lineal</b>.</p>", "aviso")
    elif vista.endswith("ln(PIB)"):
        caja("<p><b>Qué se ve.</b> Con el PIB en escala logarítmica la nube se endereza y los puntos se reparten a "
             "ambos lados de la recta en todo el recorrido. La relación es directa y fuerte: los países de la zona "
             "roja quedan abajo a la izquierda, las zonas azules arriba a la derecha y Venezuela cae cerca de la "
             "recta, un poco por encima.</p>", "clave")
    else:
        caja("<p><b>Qué se ve.</b> Es el mismo modelo 2, pero dibujado sobre el PIB en dólares: la recta en ln(PIB) "
             "se convierte en una curva logarítmica que sí acompaña el aplanamiento de la nube (rendimientos "
             "decrecientes del ingreso sobre la esperanza de vida).</p>", "clave")

# ==========================================================================
# 4. SUPUESTOS
# ==========================================================================
elif seccion == "4. Verificación de supuestos":
    titulo("4. Verificación de supuestos",
           "Linealidad, normalidad, homocedasticidad e independencia de los errores, con α = 0,05.")
    H0 = {
        "RESET de Ramsey (linealidad)": "La forma funcional lineal es correcta",
        "Shapiro-Wilk (normalidad)": "Los errores son normales",
        "Kolmogorov-Smirnov-Lilliefors (normalidad)": "Los errores son normales",
        "Jarque-Bera (normalidad)": "Los errores son normales",
        "Breusch-Pagan (homocedasticidad)": "La varianza del error es constante",
        "White (homocedasticidad)": "La varianza del error es constante",
        "Durbin-Watson (independencia)": "No hay autocorrelación de orden 1",
    }
    filas = []
    for prueba, h0 in H0.items():
        fila = {"Prueba": prueba.split(" (")[0], "Supuesto": prueba.split("(")[1].rstrip(")").capitalize(),
                "H₀": h0}
        for etiqueta, sup in (("Modelo 1", SUP_LIN), ("Modelo 2", SUP_LOG)):
            est, p = sup[prueba]
            if np.isnan(p):
                fila[f"{etiqueta}: estadístico"] = num(est, 3)
                fila[f"{etiqueta}: p"] = "—"
                fila[f"{etiqueta}: decisión"] = insignia(1.5 < est < 2.5, "Cercano a 2", "Lejos de 2")
            else:
                fila[f"{etiqueta}: estadístico"] = num(est, 3)
                fila[f"{etiqueta}: p"] = pval(p)
                fila[f"{etiqueta}: decisión"] = insignia(p >= rg.ALFA)
        filas.append(fila)
    tabla(pd.DataFrame(filas), "texto3")
    st.caption("Decisión al 5 %: se rechaza H₀ cuando p < 0,05. El estadístico de Durbin-Watson no tiene valor p "
               "directo; valores cercanos a 2 indican ausencia de autocorrelación (además, son datos de corte "
               "transversal, así que el orden de los países no tiene significado temporal).")

    st.subheader("Gráficos de residuos")
    cual = st.radio("Modelo", ["Modelo 1: Y sobre PIB", "Modelo 2: Y sobre ln(PIB)"], index=1, horizontal=True)
    if cual.startswith("Modelo 1"):
        fig_residuos(LIN, "ajustado_m1", "residuo_m1")
        st.caption("Modelo 1: los residuos no se reparten al azar. Forman un arco (suben muy rápido entre los países "
                   "pobres y caen por debajo de cero en los más ricos) y casi todos los países se amontonan en valores "
                   "ajustados bajos: señal clara de mala especificación.")
    else:
        fig_residuos(LOG, "ajustado_m2", "residuo_m2")
        st.caption("Modelo 2: los residuos se reparten alrededor de cero sin un patrón marcado; la dispersión es algo "
                   "mayor en los países de menor esperanza de vida ajustada (heterocedasticidad leve) y la cola "
                   "izquierda es un poco más pesada que la normal.")
    st.markdown(LEYENDA_GRUPOS, unsafe_allow_html=True)

    st.subheader("¿Por qué nos quedamos con el modelo logarítmico?")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        caja(
            f"<p><b>Modelo 1 (PIB en US$).</b> La prueba RESET rechaza con contundencia la linealidad "
            f"(p = {pval(SUP_LIN['RESET de Ramsey (linealidad)'][1])}) y las tres pruebas de normalidad rechazan H₀. "
            f"Con la forma funcional equivocada, a y b no describen bien la relación y solo se explica el "
            f"{num(100 * R1['r2'], 1)} % de la variación.</p>", "aviso")
    with c2:
        caja(
            f"<p><b>Modelo 2 (ln PIB).</b> R² sube de {num(R1['r2'], 4)} a {num(R2['r2'], 4)} y el error estándar baja de "
            f"{num(R1['s'], 2)} a {num(R2['s'], 2)} años. La normalidad es aceptable (Lilliefors p = "
            f"{pval(SUP_LOG['Kolmogorov-Smirnov-Lilliefors (normalidad)'][1])}; Shapiro-Wilk y Jarque-Bera quedan "
            f"apenas por debajo de 0,05) y Durbin-Watson es {num(SUP_LOG['Durbin-Watson (independencia)'][0], 2)}.</p>",
            "clave")
    st.markdown(
        f"""
**Lo que no se cumple del todo, dicho con honestidad.** En el modelo 2 queda una heterocedasticidad leve
(Breusch-Pagan p = {pval(SUP_LOG['Breusch-Pagan (homocedasticidad)'][1])}) y la prueba RESET todavía rechaza al 5 %
(p = {pval(SUP_LOG['RESET de Ramsey (linealidad)'][1])}), aunque ya no al 1 % y a una distancia enorme del modelo 1.
Por eso en la sección 7 repetimos la inferencia sobre B con errores estándar robustos HC3: la conclusión no cambia.
Con n = 100, además, las pruebas t y F son poco sensibles a desviaciones moderadas de la normalidad.
""")

# ==========================================================================
# 5. COEFICIENTES
# ==========================================================================
elif seccion == "5. Coeficientes y ecuación":
    titulo("5. Estimación de los coeficientes y ecuación de regresión",
           "Mínimos cuadrados ordinarios sobre el modelo 2, con X = ln(PIB per cápita).")
    st.latex(r"Y_i = A + B\,\ln(\text{PIB}_i) + \varepsilon_i \qquad\Longrightarrow\qquad \hat{Y} = a + b\,\ln(\text{PIB})")
    tarjetas([
        ("n", f"{R2['n']}", "países", "gris"),
        ("Media de X", num(R2["xm"], 4), "x̄, con X = ln(PIB)", "gris"),
        ("Media de Y", num(R2["ym"], 4), "ȳ, en años", "gris"),
        ("Sxx", num(R2["sxx"], 4), "Σ(x − x̄)²", "gris"),
        ("Sxy", num(R2["sxy"], 4), "Σ(x − x̄)(y − ȳ)", "gris"),
        ("Syy", num(R2["syy"], 2), "Σ(y − ȳ)²", "gris"),
    ])
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader("Pendiente")
        st.latex(r"b=\frac{S_{xy}}{S_{xx}}=\frac{\sum (x_i-\bar x)(y_i-\bar y)}{\sum (x_i-\bar x)^2}")
        st.latex(rf"b=\frac{{{ltx(R2['sxy'], 4)}}}{{{ltx(R2['sxx'], 4)}}}={ltx(R2['b'], 4)}")
    with c2:
        st.subheader("Ordenada en el origen")
        st.latex(r"a=\bar y-b\,\bar x")
        st.latex(rf"a={ltx(R2['ym'], 4)}-({ltx(R2['b'], 4)})({ltx(R2['xm'], 4)})={ltx(R2['a'], 4)}")
    st.subheader("Ecuación de regresión estimada")
    st.markdown(
        f"<div class='caja clave' style='text-align:center;font-family:Georgia,serif;font-size:1.7rem;color:#16324f;"
        f"padding:1.3rem'>Ŷ = {num(R2['a'], 4)} + {num(R2['b'], 4)} · ln(PIB per cápita)</div>",
        unsafe_allow_html=True)
    st.subheader("Error estándar de la estimación")
    st.latex(rf"s=\sqrt{{\frac{{SCE}}{{n-2}}}}=\sqrt{{\frac{{{ltx(R2['sce'], 2)}}}{{{R2['gl']}}}}}={ltx(R2['s'], 4)}\ \text{{años}}")
    with st.expander("Comparación con el modelo 1 (PIB en dólares, sin logaritmo)"):
        st.latex(rf"\hat Y = {ltx(R1['a'], 4)} + {ltx(R1['b'], 6)}\cdot \text{{PIB}}\qquad r={ltx(R1['r'], 4)},\quad R^2={ltx(R1['r2'], 4)},\quad s={ltx(R1['s'], 3)}")
        st.caption("Se calcula igual, pero no se usa para inferir porque no cumple el supuesto de linealidad (sección 4).")

# ==========================================================================
# 6. INTERPRETACIÓN
# ==========================================================================
elif seccion == "6. Interpretación de a y b":
    titulo("6. Interpretación de a y b", "Qué significan los coeficientes cuando X está en logaritmos.")
    b = R2["b"]
    tarjetas([
        ("+1 % de PIB per cápita", f"+{num(b / 100, 4)}", "años de esperanza de vida (≈ b/100)"),
        ("+10 % de PIB per cápita", f"+{num(b * np.log(1.1), 2)}", "años (b · ln 1,1)"),
        ("Duplicar el PIB per cápita", f"+{num(b * np.log(2), 2)}", "años (b · ln 2)", "verde"),
        ("Multiplicarlo por 10", f"+{num(b * np.log(10), 2)}", "años (b · ln 10)"),
    ])
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader(f"Pendiente b = {num(b, 4)}")
        st.markdown(
            f"""
Por cada unidad que aumenta ln(PIB), la esperanza de vida media aumenta **{num(b, 2)} años**. Como una unidad de
logaritmo equivale a multiplicar el PIB por *e* ≈ 2,72, es más cómodo leerla en porcentajes:

- un aumento de **1 %** en el PIB per cápita se asocia con unos **{num(b / 100, 3)} años** más
  (alrededor de {num(b / 100 * 365, 0)} días);
- un aumento de **10 %**, con **{num(b * np.log(1.1), 2)} años** más;
- **duplicar** el PIB per cápita, con **{num(b * np.log(2), 2)} años** más, sin importar el nivel de partida.

El signo positivo indica una relación directa. El efecto es *relativo*: pasar de US$ 1.000 a US$ 2.000 «vale» lo
mismo que pasar de US$ 40.000 a US$ 80.000.
""")
        st.latex(rf"\Delta\hat Y = b\,\ln\!\left(\frac{{\text{{PIB}}_1}}{{\text{{PIB}}_0}}\right)\;\Rightarrow\; {ltx(b, 4)}\cdot\ln 2 = {ltx(b * np.log(2), 2)}\ \text{{años}}")
    with c2:
        st.subheader(f"Ordenada a = {num(R2['a'], 4)}")
        st.markdown(
            f"""
Es la esperanza de vida estimada cuando ln(PIB) = 0, es decir, para un país con un PIB per cápita de **US$ 1**:
{num(R2['a'], 1)} años.

Ese valor **no tiene interpretación práctica**: el menor PIB per cápita de la muestra es de
US$ {num(df[X].min(), 1)} ({df.loc[df[X].idxmin(), 'pais']}), muy lejos de US$ 1, así que sería una extrapolación.
La constante sirve para ubicar la recta, no para describir un país real.
""")
        caja("<p><b>Cuidado con la causalidad.</b> El modelo describe una asociación entre países en un mismo año. "
             "No demuestra que aumentar el ingreso <i>cause</i> por sí solo más años de vida: salud pública, "
             "educación, conflictos y desigualdad también influyen y están correlacionados con el PIB.</p>", "aviso")

# ==========================================================================
# 7. INFERENCIAS A y B
# ==========================================================================
elif seccion == "7. Inferencias sobre A y B":
    titulo("7. Inferencias sobre los parámetros A y B",
           f"Pruebas t bilaterales con α = 0,05 y {R2['gl']} grados de libertad (modelo 2).")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader("Pendiente B")
        st.latex(r"H_0: B = 0 \qquad H_1: B \neq 0")
        st.latex(rf"s_b=\frac{{s}}{{\sqrt{{S_{{xx}}}}}}={ltx(R2['se_b'], 4)}")
        st.latex(rf"t=\frac{{b}}{{s_b}}=\frac{{{ltx(R2['b'], 4)}}}{{{ltx(R2['se_b'], 4)}}}={ltx(R2['t_b'], 2)}")
    with c2:
        st.subheader("Ordenada A")
        st.latex(r"H_0: A = 0 \qquad H_1: A \neq 0")
        st.latex(rf"s_a=s\sqrt{{\tfrac1n+\tfrac{{\bar x^2}}{{S_{{xx}}}}}}={ltx(R2['se_a'], 4)}")
        st.latex(rf"t=\frac{{a}}{{s_a}}=\frac{{{ltx(R2['a'], 4)}}}{{{ltx(R2['se_a'], 4)}}}={ltx(R2['t_a'], 2)}")
    filas = []
    for nom, k in (("A (ordenada)", "a"), ("B (pendiente)", "b")):
        filas.append({
            "Parámetro": nom, "Estimación": num(R2[k], 4), "Error estándar": num(R2[f"se_{k}"], 4),
            "t calculado": num(R2[f"t_{k}"], 2), "t crítico (±)": num(R2["tcrit"], 4),
            "Valor p": pval(R2[f"p_{k}"]), "IC 95 %": ic(R2[f"ic_{k}"], 4),
            "Decisión": insignia(abs(R2[f"t_{k}"]) <= R2["tcrit"]),
        })
    tabla(pd.DataFrame(filas))
    caja(
        f"<p><b>Decisión.</b> Como |t| = {num(R2['t_b'], 2)} &gt; {num(R2['tcrit'], 3)} (p = {pval(R2['p_b'])}), se rechaza "
        f"H₀: B = 0. Hay evidencia muy fuerte de que el PIB per cápita (en logaritmo) aporta a explicar la esperanza de "
        f"vida. Con 95 % de confianza, B está entre {num(R2['ic_b'][0], 2)} y {num(R2['ic_b'][1], 2)}: duplicar el PIB "
        f"se asocia con entre {num(R2['ic_b'][0] * np.log(2), 2)} y {num(R2['ic_b'][1] * np.log(2), 2)} años más de vida. "
        f"También se rechaza H₀: A = 0, aunque la ordenada no tiene lectura práctica.</p>", "clave")

    st.subheader("Comprobación con errores estándar robustos (HC3)")
    st.markdown(
        "Como en la sección 4 apareció una heterocedasticidad leve, repetimos la inferencia con errores estándar "
        "robustos HC3, que no exigen varianza constante. Las estimaciones puntuales son las mismas; solo cambian "
        "los errores estándar.")
    h = LOG.ols_hc3
    ich = h.conf_int()
    filas = []
    for i, (nom, k) in enumerate((("A (ordenada)", "a"), ("B (pendiente)", "b"))):
        filas.append({
            "Parámetro": nom, "Estimación": num(R2[k], 4),
            "Error estándar clásico": num(R2[f"se_{k}"], 4), "Error estándar HC3": num(h.bse[i], 4),
            "t con HC3": num(h.tvalues[i], 2), "Valor p (HC3)": pval(h.pvalues[i]),
            "IC 95 % (HC3)": ic(ich[i], 4), "Decisión": insignia(h.pvalues[i] >= rg.ALFA),
        })
    tabla(pd.DataFrame(filas))
    st.caption(f"Con HC3 el error estándar de b pasa de {num(R2['se_b'], 4)} a {num(h.bse[1], 4)} y t sigue siendo "
               f"{num(h.tvalues[1], 2)}: la pendiente continúa siendo muy significativa.")

# ==========================================================================
# 8. INTERVALOS
# ==========================================================================
elif seccion == "8. Intervalos y predicción":
    titulo("8. Intervalos para μ y|x y para un valor particular Yₐ",
           "Predicción interactiva con el modelo 2: elija un país o escriba un PIB per cápita.")
    c1, c2, c3 = st.columns([2, 3, 2])
    modo = c1.radio("Valor de X", ["País de la muestra", "PIB libre"], horizontal=False)
    paises = sorted(df["pais"])
    if modo == "País de la muestra":
        pais = c2.selectbox("País", paises, index=paises.index("Venezuela"))
        fila = df[df["pais"] == pais].iloc[0]
        pib, obs = float(fila[X]), float(fila[Y])
    else:
        pais, obs = None, None
        pib = c2.number_input("PIB per cápita (US$ corrientes)", min_value=100.0, max_value=250000.0,
                              value=float(VEN[X]), step=500.0, format="%.1f")
    nivel = c3.radio("Nivel de confianza", [0.90, 0.95, 0.99], index=1, horizontal=True,
                     format_func=lambda v: f"{int(v * 100)} %")
    y0, icm, icp, t, iv = intervalos_nivel(LOG, pib, nivel)
    y0 = float(y0)
    pct = f"{int(nivel * 100)} %"
    fuera = pib < df[X].min() or pib > df[X].max()

    items = [
        ("PIB per cápita", f"US$ {num(pib, 1)}", pais or "valor elegido", "gris"),
        ("Estimación puntual Ŷ", num(y0, 2), "años"),
        (f"IC {pct} para la media", f"<span style='font-size:1.3rem;white-space:nowrap'>{ic(icm)}</span>", f"amplitud {num(icm[1] - icm[0], 2)} años"),
        (f"IC {pct} de predicción", f"<span style='font-size:1.3rem;white-space:nowrap'>{ic(icp)}</span>", f"amplitud {num(icp[1] - icp[0], 2)} años"),
    ]
    if obs is not None:
        dentro = icp[0] <= obs <= icp[1]
        items.append(("Valor observado", num(obs, 2),
                      f"residuo {num(obs - y0, 2) if obs < y0 else '+' + num(obs - y0, 2)} años · "
                      + ("dentro" if dentro else "fuera") + " del intervalo de predicción",
                      "verde" if dentro else "naranja"))
    tarjetas(items)
    if fuera:
        st.warning(f"Ese PIB está fuera del rango de la muestra (US$ {num(df[X].min(), 1)} a US$ {num(df[X].max(), 1)}): "
                   "la predicción es una extrapolación y debe tomarse con cautela.")

    g1, g2 = st.columns([3, 2], gap="large")
    with g1:
        f = fig_dispersion(LOG, True, True, True, nivel=nivel, alto=500, leyenda=False)
        f.layout.annotations = ()
        for tr in f.data:
            if tr.mode and "markers" in tr.mode:
                tr.marker.opacity = 0.45
                tr.showlegend = False
        f.add_trace(go.Scatter(x=[pib, pib], y=list(icp), mode="lines+markers", name=f"Predicción {pct}",
                               line=dict(color="#16324f", width=2), marker=dict(symbol="line-ew", size=14,
                               line=dict(color="#16324f", width=2)), hoverinfo="skip"))
        f.add_trace(go.Scatter(x=[pib, pib], y=list(icm), mode="lines", name=f"Media {pct}",
                               line=dict(color="#16324f", width=7), hoverinfo="skip"))
        f.add_trace(go.Scatter(x=[pib], y=[y0], mode="markers", name="Ŷ",
                               marker=dict(color="#ffffff", size=11, line=dict(color="#16324f", width=2.5)),
                               hovertemplate=f"Ŷ = {num(y0, 2)} años<extra></extra>"))
        if obs is not None:
            f.add_trace(go.Scatter(x=[pib], y=[obs], mode="markers", name="Observado",
                                   marker=dict(color=COLOR_GRUPO["Venezuela"], size=15, symbol="star",
                                               line=dict(color="#fff", width=1.2)),
                                   hovertemplate=f"<b>{pais}</b><br>Observado: {num(obs, 2)} años<extra></extra>"))
        f.add_annotation(x=np.log10(pib), y=icp[1], yshift=14, showarrow=False,
                         text=f"<b>{pais or 'PIB elegido'}</b>", font=dict(size=13, color=TINTA),
                         bgcolor="rgba(255,255,255,0.85)")
        mostrar(f, "pred")
        st.caption(f"Barra gruesa: intervalo de confianza para la media. Barra fina: intervalo de predicción. "
                   f"Círculo blanco: Ŷ. " + ("Estrella verde: valor observado. " if obs is not None else "")
                   + f"Las bandas sombreadas son los mismos intervalos, al {pct}, para todo el recorrido del PIB.")
    with g2:
        st.markdown(f"**Cálculo con t({R2['gl']}) = {num(t, 4)} al {pct}**")
        st.latex(rf"\hat Y_0 = {ltx(R2['a'], 4)} + {ltx(R2['b'], 4)}\cdot\ln({ltx(pib, 1)}) = {ltx(y0, 2)}")
        st.markdown("Intervalo de confianza para la media μ y|x₀:")
        st.latex(r"\hat Y_0 \pm t_{\alpha/2}\; s\sqrt{\frac1n+\frac{(x_0-\bar x)^2}{S_{xx}}}")
        st.latex(rf"{ltx(y0, 2)} \pm {ltx(t, 4)}\,({ltx(float(iv['se_media']), 4)}) = ({ltx(icm[0], 2)};\ {ltx(icm[1], 2)})")
        st.markdown("Intervalo de predicción para un valor particular Yₐ:")
        st.latex(r"\hat Y_0 \pm t_{\alpha/2}\; s\sqrt{1+\frac1n+\frac{(x_0-\bar x)^2}{S_{xx}}}")
        st.latex(rf"{ltx(y0, 2)} \pm {ltx(t, 4)}\,({ltx(float(iv['se_pred']), 4)}) = ({ltx(icp[0], 2)};\ {ltx(icp[1], 2)})")

    quien = f"como {pais}" if pais else "con ese ingreso"
    caja(
        f"<p><b>Interpretación.</b> Con {pct} de confianza, la esperanza de vida <i>promedio</i> de todos los países con un "
        f"PIB per cápita de US$ {num(pib, 1)} está entre {num(icm[0], 2)} y {num(icm[1], 2)} años. Para <i>un país en "
        f"particular</i> {quien}, el valor individual estaría entre {num(icp[0], 2)} y {num(icp[1], 2)} años. El segundo "
        f"intervalo es mucho más ancho porque suma la variabilidad propia de cada país (s = {num(R2['s'], 3)}) a la "
        f"incertidumbre de la recta."
        + (f" El valor observado de {pais}, {num(obs, 2)} años, "
           + ("cae dentro del intervalo de predicción." if icp[0] <= obs <= icp[1]
              else "queda fuera del intervalo de predicción: es un país atípico para su nivel de ingreso.")
           if obs is not None else "")
        + "</p>", "clave")
    if abs(nivel - 0.95) > 1e-9:
        st.caption("El informe escrito usa 95 %. Para otros niveles se aplican las mismas fórmulas cambiando solo el "
                   "valor crítico de t.")

# ==========================================================================
# 9. RHO
# ==========================================================================
elif seccion == "9. Inferencias sobre ρ":
    titulo("9. Inferencias sobre el coeficiente de correlación ρ",
           "Correlación de Pearson entre ln(PIB per cápita) y esperanza de vida.")
    tarjetas([
        ("r muestral", num(R2["r"], 4), "correlación directa y fuerte"),
        ("t calculado", num(R2["t_r"], 2), f"t crítico ± {num(R2['tcrit'], 4)}"),
        ("Valor p", pval(R2["p_r"]), "prueba bilateral"),
        ("IC 95 % para ρ", f"<span style='font-size:1.3rem;white-space:nowrap'>{ic(R2['ic_rho'], 4)}</span>", "transformación z de Fisher", "verde"),
    ])
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader("Prueba de hipótesis")
        st.latex(r"H_0: \rho = 0 \qquad H_1: \rho \neq 0")
        st.latex(r"r=\frac{S_{xy}}{\sqrt{S_{xx}\,S_{yy}}}\qquad t=\frac{r\sqrt{n-2}}{\sqrt{1-r^2}}")
        st.latex(rf"t=\frac{{{ltx(R2['r'], 4)}\sqrt{{{R2['gl']}}}}}{{\sqrt{{1-{ltx(R2['r2'], 4)}}}}}={ltx(R2['t_r'], 2)}")
        st.markdown(
            f"Como {num(R2['t_r'], 2)} > {num(R2['tcrit'], 3)}, **se rechaza H₀**: la correlación poblacional es "
            f"distinta de cero. En regresión simple este t es el mismo de la prueba sobre B "
            f"(t = {num(R2['t_b'], 2)}).")
    with c2:
        st.subheader("Intervalo de confianza (z de Fisher)")
        zc = stats.norm.ppf(1 - rg.ALFA / 2)
        st.latex(r"z_r=\tfrac12\ln\!\left(\frac{1+r}{1-r}\right)\qquad z_r \pm z_{\alpha/2}\,\frac{1}{\sqrt{n-3}}")
        st.latex(rf"z_r={ltx(R2['z_fisher'], 4)}\qquad {ltx(R2['z_fisher'], 4)}\pm {ltx(zc, 2)}\cdot\frac{{1}}{{\sqrt{{{R2['n'] - 3}}}}}")
        st.latex(rf"\rho\in({ltx(R2['ic_rho'][0], 4)};\ {ltx(R2['ic_rho'][1], 4)})")
        st.markdown(
            f"Con 95 % de confianza, ρ está entre {num(R2['ic_rho'][0], 2)} y {num(R2['ic_rho'][1], 2)}. "
            f"Todo el intervalo está por encima de 0,8: la asociación es fuerte aun en el extremo inferior.")
    with st.expander("Comparación con el modelo 1"):
        st.markdown(
            f"Entre el PIB en dólares (sin logaritmo) y la esperanza de vida, r = {num(R1['r'], 4)} con IC 95 % "
            f"{ic(R1['ic_rho'], 4)}. Es menor porque r solo mide asociación *lineal* y esa relación es curva.")

# ==========================================================================
# 10. R2
# ==========================================================================
elif seccion == "10. Coeficiente de determinación":
    titulo("10. Coeficiente de determinación", "Qué parte de la variación de la esperanza de vida explica el modelo.")
    tarjetas([
        ("R²", num(R2["r2"], 4), f"{num(100 * R2['r2'], 2)} % explicado", "verde"),
        ("R² ajustado", num(R2["r2_aj"], 4), "corregido por grados de libertad"),
        ("SCR (regresión)", num(R2["scr"], 2), "variación explicada"),
        ("SCE (error)", num(R2["sce"], 2), "variación no explicada", "naranja"),
        ("SCT (total)", num(R2["sct"], 2), "Σ(y − ȳ)²", "gris"),
    ])
    st.latex(rf"R^2=\frac{{SCR}}{{SCT}}=1-\frac{{SCE}}{{SCT}}=\frac{{{ltx(R2['scr'], 2)}}}{{{ltx(R2['sct'], 2)}}}={ltx(R2['r2'], 4)}"
             rf"\qquad \bar R^2 = 1-(1-R^2)\frac{{n-1}}{{n-2}}={ltx(R2['r2_aj'], 4)}")
    st.subheader("Descomposición de la variación total: SCT = SCR + SCE")
    f = go.Figure()
    etiquetas = ["Modelo 1: PIB", "Modelo 2: ln(PIB)"]
    scr = [R1["scr"], R2["scr"]]
    sce = [R1["sce"], R2["sce"]]
    sct = [R1["sct"], R2["sct"]]
    f.add_trace(go.Bar(y=etiquetas, x=scr, orientation="h", name="SCR: explicada por la regresión",
                       marker=dict(color="#1f4e79", line=dict(color="#fbfaf7", width=2)),
                       text=[f"SCR = {num(a, 1)}  ({num(100 * a / t, 1)} %)" for a, t in zip(scr, sct)],
                       textposition="inside", insidetextanchor="middle", textfont=dict(color="#fff", size=14),
                       hovertemplate="SCR = %{x:,.2f}<extra></extra>"))
    f.add_trace(go.Bar(y=etiquetas, x=sce, orientation="h", name="SCE: no explicada (error)",
                       marker=dict(color="#d9d5cb", line=dict(color="#fbfaf7", width=2)),
                       text=[f"SCE = {num(a, 1)}  ({num(100 * a / t, 1)} %)" for a, t in zip(sce, sct)],
                       textposition="inside", insidetextanchor="middle", textfont=dict(color=TINTA, size=14),
                       hovertemplate="SCE = %{x:,.2f}<extra></extra>"))
    estilo(f, 270)
    f.update_layout(barmode="stack", bargap=0.35, margin_l=150, legend_traceorder="normal")
    f.update_xaxes(title_text=f"Suma de cuadrados (SCT = {num(R2['sct'], 2)})", tickformat=",.0f")
    f.update_yaxes(autorange="reversed", showgrid=False)
    mostrar(f, "sc")
    caja(
        f"<p><b>Interpretación.</b> El {num(100 * R2['r2'], 1)} % de la variación de la esperanza de vida entre los 100 "
        f"países se explica por su relación lineal con el logaritmo del PIB per cápita; el {num(100 * (1 - R2['r2']), 1)} % "
        f"restante se debe a otros factores que el modelo no incluye (sistema de salud, educación, conflictos, "
        f"desigualdad, VIH, etc.). El mismo cambio de variable casi duplica lo explicado frente al modelo 1 "
        f"({num(100 * R1['r2'], 1)} %). Se cumple además que R² = r²: ({num(R2['r'], 4)})² = {num(R2['r2'], 4)}.</p>", "clave")

# ==========================================================================
# 11. ANOVA
# ==========================================================================
elif seccion == "11. Análisis de varianza":
    titulo("11. Análisis de varianza (ANOVA)", "Prueba F de significación global de la regresión (modelo 2).")
    st.latex(r"H_0: B = 0\ \ (\text{la regresión no es significativa}) \qquad H_1: B \neq 0")
    an = LOG.anova()
    filas = []
    for _, f_ in an.iterrows():
        filas.append({
            "Fuente de variación": f_["Fuente de variación"],
            "Suma de cuadrados": num(f_["Suma de cuadrados"], 2),
            "Grados de libertad": f"{int(f_['Grados de libertad'])}",
            "Cuadrado medio": num(f_["Cuadrado medio"], 2),
            "F calculado": num(f_["F calculado"], 2),
            "Valor p": pval(f_["Valor p"]),
        })
    tabla(pd.DataFrame(filas))
    tarjetas([
        ("F calculado", num(R2["F"], 2), "CMR / CME"),
        (f"F crítico (1; {R2['gl']}; 0,05)", num(R2["Fcrit"], 4), "región de rechazo: F > F crítico", "gris"),
        ("Valor p", pval(R2["p_F"]), "prácticamente cero"),
        ("Decisión", "Se rechaza H₀", "la regresión es significativa", "verde"),
    ])
    st.latex(rf"F=\frac{{CMR}}{{CME}}=\frac{{SCR/1}}{{SCE/(n-2)}}=\frac{{{ltx(R2['scr'], 2)}}}{{{ltx(R2['s2'], 4)}}}={ltx(R2['F'], 2)}")
    caja(
        f"<p><b>Decisión.</b> Como F = {num(R2['F'], 2)} es muchísimo mayor que el F crítico de {num(R2['Fcrit'], 2)}, se "
        f"rechaza H₀ al 5 %: el modelo de regresión es significativo en su conjunto.</p>"
        f"<p><b>Nota.</b> En regresión simple la prueba F y la prueba t sobre B son equivalentes: "
        f"F = t², es decir, ({num(R2['t_b'], 4)})² = {num(R2['t_b'] ** 2, 2)}, y el F crítico es el cuadrado del t "
        f"crítico: ({num(R2['tcrit'], 4)})² = {num(R2['tcrit'] ** 2, 4)}.</p>", "clave")
    with st.expander("ANOVA del modelo 1 (referencia)"):
        an1 = LIN.anova()
        tabla(pd.DataFrame([{
            "Fuente de variación": f_["Fuente de variación"], "Suma de cuadrados": num(f_["Suma de cuadrados"], 2),
            "Grados de libertad": f"{int(f_['Grados de libertad'])}", "Cuadrado medio": num(f_["Cuadrado medio"], 2),
            "F calculado": num(f_["F calculado"], 2), "Valor p": pval(f_["Valor p"])} for _, f_ in an1.iterrows()]))

# ==========================================================================
# CONCLUSIONES
# ==========================================================================
else:
    titulo("Conclusiones")
    ivv = LOG.intervalos(VEN[X])
    st.markdown(
        f"""
1. **Sí hay relación, y es fuerte.** Entre los 100 países, la esperanza de vida aumenta con el PIB per cápita:
   r = {num(R2['r'], 4)} entre ln(PIB) y esperanza de vida, con IC 95 % para ρ de {ic(R2['ic_rho'], 2)}.
2. **La relación es logarítmica, no lineal.** El modelo con el PIB en dólares falla la prueba de linealidad
   (RESET p = {pval(SUP_LIN['RESET de Ramsey (linealidad)'][1])}) y explica solo el {num(100 * R1['r2'], 1)} %.
   Con ln(PIB) la ecuación es **Ŷ = {num(R2['a'], 4)} + {num(R2['b'], 4)} · ln(PIB)** y R² = {num(R2['r2'], 4)}.
3. **Rendimientos decrecientes.** Duplicar el PIB per cápita se asocia con unos {num(R2['b'] * np.log(2), 2)} años
   más de vida, tanto si se parte de US$ 1.000 como de US$ 40.000: cada dólar adicional rinde mucho más en los
   países pobres.
4. **El modelo es significativo.** t = {num(R2['t_b'], 2)} para B y F = {num(R2['F'], 2)} (p ≈ 0); la conclusión se
   mantiene con errores robustos HC3, que usamos por la heterocedasticidad leve detectada.
5. **Venezuela está donde el modelo espera, un poco por encima.** Con US$ {num(VEN[X], 1)} el modelo estima
   {num(float(ivv['y0']), 2)} años (IC 95 % de la media {ic(ivv['ic_media'])}; predicción {ic(ivv['ic_pred'])}) y el
   valor observado es {num(VEN[Y], 2)} años.
6. **Limitaciones.** Un {num(100 * (1 - R2['r2']), 1)} % de la variación queda sin explicar, los supuestos del modelo 2
   se cumplen solo de forma aproximada (normalidad en el límite, heterocedasticidad leve y RESET con
   p = {pval(SUP_LOG['RESET de Ramsey (linealidad)'][1])}) y, sobre todo, asociación no implica causalidad:
   es un corte transversal de un solo año.
""")
    st.subheader("Fuente de los datos")
    st.markdown(
        """
Banco Mundial, *Indicadores del Desarrollo Mundial* (World Development Indicators). Datos descargados el 15/11/2026.

- **NY.GDP.PCAP.CD**: PIB per cápita (US$ a precios actuales), 2024.
- **SP.DYN.LE00.IN**: esperanza de vida al nacer, total (años), 2024.

Procesamiento y cálculos en Python (pandas, NumPy, SciPy y statsmodels) con las fórmulas del curso; gráficos con Plotly.
""")

st.markdown(
    "<div class='pie-pagina'>Estadística II · Escuela de Estadística y Ciencias Actuariales, UCV · "
    "Allan Arcia y Eddie Palomino · Profesoras Sandra Pinto y Yuraisi Capriles · "
    "Fuente: Banco Mundial, Indicadores del Desarrollo Mundial (2024)</div>",
    unsafe_allow_html=True)
