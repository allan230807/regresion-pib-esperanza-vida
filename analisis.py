"""Análisis completo: genera las figuras del informe y un resumen en consola.
Uso: python analisis.py  (desde la raíz del repositorio)"""
import sys, os
sys.path.insert(0, "src")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from scipy import stats
from regresion import cargar_datos, modelos, descriptivas

os.makedirs("figuras", exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e5e1",
                     "grid.linewidth": .6, "axes.edgecolor": "#8a8984", "axes.axisbelow": True,
                     "figure.dpi": 100, "savefig.dpi": 200, "savefig.bbox": "tight"})
AZUL, NARANJA, AQUA, GRIS, TINTA = "#2a78d6", "#eb6834", "#1baf7a", "#a3a29c", "#2b2a27"
COLORES = {"Otro": GRIS, "Zona azul": AZUL, "Zona roja": NARANJA, "Venezuela": AQUA}

df = cargar_datos()
lin, log = modelos(df)
y = df["esperanza_vida_2024"]

def guardar(nombre):
    plt.savefig(f"figuras/{nombre}.png"); plt.close()

# Fig 1: histogramas
fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
for a, col, t in zip(ax, ["pib_pc_usd_2024", "ln_pib_pc", "esperanza_vida_2024"],
                     ["PIB per cápita (US$)", "ln(PIB per cápita)", "Esperanza de vida (años)"]):
    a.hist(df[col], bins=14, color=AZUL, edgecolor="white", linewidth=1.5)
    a.axvline(df[col].mean(), color=TINTA, lw=1.2, ls="--", label="Media")
    a.axvline(df[col].median(), color=NARANJA, lw=1.2, label="Mediana")
    a.set_xlabel(t); a.set_ylabel("Países")
ax[0].legend(frameon=False)
ax[0].xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
fig.subplots_adjust(wspace=.3)
guardar("fig01_histogramas")

# Fig 2: boxplots por nivel de ingreso
orden = ["Ingreso bajo", "Ingreso mediano bajo", "Ingreso mediano alto", "Ingreso alto"]
fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
for a, col, t in zip(ax, ["pib_pc_usd_2024", "esperanza_vida_2024"], ["PIB per cápita (US$)", "Esperanza de vida (años)"]):
    data = [df.loc[df.ingreso == g, col] for g in orden]
    bp = a.boxplot(data, patch_artist=True, widths=.5, medianprops=dict(color=TINTA, lw=1.5))
    for p in bp["boxes"]: p.set(facecolor="#cfe0f5", edgecolor=AZUL)
    a.set_xticks(range(1, 5), ["Bajo", "Mediano\nbajo", "Mediano\nalto", "Alto"]); a.set_ylabel(t)
    a.set_xlabel("Nivel de ingreso (Banco Mundial)")
    a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
guardar("fig02_boxplots_ingreso")

# Fig 3 y 4: dispersión con recta (modelo 1 y 2)
def dispersion(m, nombre, xlabel, escala_log):
    fig, a = plt.subplots(figsize=(8.5, 5.2))
    pib = df["pib_pc_usd_2024"]
    grid = np.linspace(pib.min() * .9, pib.max() * 1.05, 400)
    iv = m.intervalos(grid)
    a.fill_between(grid, *iv["ic_pred"], color=AZUL, alpha=.08, lw=0, label="IC 95 % predicción (Ya)")
    a.fill_between(grid, *iv["ic_media"], color=AZUL, alpha=.22, lw=0, label="IC 95 % media (μy|x)")
    a.plot(grid, iv["y0"], color=AZUL, lw=2, label="Recta estimada")
    for g in ["Otro", "Zona azul", "Zona roja", "Venezuela"]:
        d = df[df.grupo == g]
        a.scatter(d.pib_pc_usd_2024, d.esperanza_vida_2024, s=46 if g != "Otro" else 30, c=COLORES[g],
                  edgecolor="white", linewidth=1, zorder=3, label=g if g != "Otro" else "Resto de países")
    etiquetas = {"Venezuela": (6, -10), "Japón": (-30, 6), "Italia": (5, 4), "Grecia": (5, 4),
                 "Costa Rica": (-58, 4), "Estados Unidos": (6, -3), "Nigeria": (6, -3),
                 "Chad": (-26, -3), "Somalia": (7, -4)}
    for _, r in df[df.pais.isin(etiquetas)].iterrows():
        a.annotate(r.pais, (r.pib_pc_usd_2024, r.esperanza_vida_2024), xytext=etiquetas[r.pais],
                   textcoords="offset points", fontsize=8, color="#3d3c39")
    if escala_log:
        a.set_xscale("log")
        a.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
    else:
        a.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
    a.set_xlabel(xlabel); a.set_ylabel("Esperanza de vida al nacer (años)")
    a.set_ylim(50, 90)
    a.legend(frameon=False, fontsize=8, loc="lower right")
    guardar(nombre)
dispersion(lin, "fig03_dispersion_lineal", "PIB per cápita 2024 (US$)", False)
dispersion(log, "fig04_dispersion_log", "PIB per cápita 2024 (US$, escala logarítmica)", True)

# Fig 5 y 6: diagnóstico de residuos
def diagnostico(m, nombre):
    e, yh = m.res["e"], m.res["yhat"]
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.3))
    ax[0].scatter(yh, e, s=22, c=AZUL, edgecolor="white", linewidth=.8)
    ax[0].axhline(0, color=TINTA, lw=1); ax[0].set_xlabel("Valores ajustados (Ŷ)"); ax[0].set_ylabel("Residuos")
    ax[0].set_title("Residuos vs ajustados", fontsize=10)
    (osm, osr), (sl, ic, _) = stats.probplot(e, dist="norm")
    ax[1].scatter(osm, osr, s=22, c=AZUL, edgecolor="white", linewidth=.8)
    ax[1].plot(osm, sl * osm + ic, color=NARANJA, lw=1.5)
    ax[1].set_xlabel("Cuantiles teóricos N(0,1)"); ax[1].set_ylabel("Residuos ordenados"); ax[1].set_title("Gráfico Q-Q normal", fontsize=10)
    ax[2].hist(e, bins=14, density=True, color=AZUL, edgecolor="white", linewidth=1.5)
    xs = np.linspace(e.min(), e.max(), 200); ax[2].plot(xs, stats.norm.pdf(xs, 0, e.std(ddof=1)), color=NARANJA, lw=1.5)
    ax[2].set_xlabel("Residuos"); ax[2].set_ylabel("Densidad"); ax[2].set_title("Histograma de residuos", fontsize=10)
    fig.subplots_adjust(wspace=.38)
    guardar(nombre)
diagnostico(lin, "fig05_residuos_lineal")
diagnostico(log, "fig06_residuos_log")

# Fig 7: descomposición de la variación (ANOVA)
r = log.res
fig, a = plt.subplots(figsize=(7.5, 1.6))
a.barh([0], [r["scr"]], color=AZUL, height=.5); a.barh([0], [r["sce"]], left=[r["scr"]], color=GRIS, height=.5)
a.text(r["scr"] / 2, 0, f"SCR = {r['scr']:,.1f}  ({100*r['r2']:.1f} %)".replace(",", "X").replace(".", ",").replace("X", "."), ha="center", va="center", color="white", fontsize=9)
a.text(r["scr"] + r["sce"] / 2, 0, f"SCE = {r['sce']:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."), ha="center", va="center", color=TINTA, fontsize=9)
a.set_yticks([]); a.set_xlabel("Suma de cuadrados (SCT = 5.638,7)"); a.grid(False)
guardar("fig07_descomposicion")

print(f"Modelo 1: Y = {lin.res['a']:.4f} + {lin.res['b']:.6f} X   R2 = {lin.res['r2']:.4f}")
print(f"Modelo 2: Y = {log.res['a']:.4f} + {log.res['b']:.4f} ln(X)   R2 = {log.res['r2']:.4f}")
print("Figuras guardadas en figuras/")
