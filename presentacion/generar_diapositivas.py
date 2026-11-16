"""Genera el respaldo en PDF de la exposición (diapositivas 16:9).
Uso: python presentacion/generar_diapositivas.py  (requiere playwright con chromium)"""
import sys, base64
sys.path.insert(0, "src")
import numpy as np
from regresion import cargar_datos, modelos

df = cargar_datos(); lin, log = modelos(df); L, G = lin.res, log.res
def f(x, d=2): return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
def img(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
iv = log.intervalos(4244.5); s2 = log.supuestos()

css = """
@page { size: 13.333in 7.5in; margin: 0 }
* { box-sizing: border-box; margin: 0; padding: 0 }
body { font-family: 'Liberation Serif', 'Times New Roman', serif; color: #1d1d1b; }
.s { width: 13.333in; height: 7.5in; padding: .55in .75in; page-break-after: always; position: relative; background: #fff; overflow: hidden }
.s:last-child { page-break-after: auto }
h1 { font-size: 34pt; color: #12355b; margin-bottom: .2in }
h2 { font-size: 26pt; color: #12355b; border-bottom: 3px solid #2a78d6; padding-bottom: .08in; margin-bottom: .25in }
p, li { font-size: 17pt; line-height: 1.4 }
li { margin: .06in 0 .06in .3in }
.pie { position: absolute; bottom: .25in; right: .75in; font-size: 10pt; color: #777 }
.dos { display: grid; grid-template-columns: 1.35fr 1fr; gap: .35in; align-items: center }
.eq { font-size: 24pt; text-align: center; background: #eef4fc; padding: .18in; border-radius: 8px; margin: .15in 0; font-style: italic }
table { border-collapse: collapse; font-size: 15pt; width: 100% }
th, td { border: 1px solid #b9c7da; padding: .05in .12in; text-align: center }
th { background: #d9e2f3 }
td:first-child { text-align: left }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: .2in; margin: .25in 0 }
.k { background: #eef4fc; border-radius: 8px; padding: .15in; text-align: center }
.k b { display: block; font-size: 30pt; color: #12355b } .k span { font-size: 12pt; color: #555 }
.portada { background: #12355b; color: #fff; display: flex; flex-direction: column; justify-content: center }
.portada h1 { color: #fff; font-size: 40pt } .portada p { font-size: 16pt; color: #dfe8f5 }
"""
S = []
S.append(f"""<div class="s portada"><p>Universidad Central de Venezuela · Facultad de Ciencias Económicas y Sociales<br>Escuela de Estadística y Ciencias Actuariales · Estadística II</p><br>
<h1>¿Los países más ricos viven más?</h1><p style="font-size:22pt">Regresión lineal bivariante: PIB per cápita y esperanza de vida al nacer en 100 países (2024)</p><br><br>
<p>Autores: Allan Arcia y Eddie Palomino<br>Profesoras: Sandra Pinto y Yuraisi Capriles</p></div>""")
S.append(f"""<div class="s"><h2>1. Datos</h2><ul>
<li><b>Fuente única:</b> Banco Mundial, Indicadores del Desarrollo Mundial (2024)</li>
<li><b>X</b> = PIB per cápita, US$ corrientes (NY.GDP.PCAP.CD)</li>
<li><b>Y</b> = esperanza de vida al nacer, años (SP.DYN.LE00.IN)</li>
<li><b>n = 100 países</b> de todas las regiones y niveles de ingreso, incluyendo Venezuela, las zonas azules (Japón, Italia, Grecia, Costa Rica, EE.&nbsp;UU.) y 10 "zonas rojas" de baja esperanza de vida</li></ul>
<div class="kpis"><div class="k"><b>{f(df.pib_pc_usd_2024.mean(),0)}</b><span>PIB pc medio (US$)</span></div><div class="k"><b>{f(df.pib_pc_usd_2024.median(),0)}</b><span>PIB pc mediano (US$)</span></div>
<div class="k"><b>{f(df.esperanza_vida_2024.mean(),1)}</b><span>Esperanza de vida media</span></div><div class="k"><b>54,6 a 84,4</b><span>Rango de esperanza de vida</span></div></div><div class="pie">Estadística II · UCV</div></div>""")
S.append(f"""<div class="s"><h2>2. Estadísticas descriptivas</h2><img src="{img('figuras/fig01_histogramas.png')}" style="width:100%"><br><br>
<p>El PIB es muy asimétrico (asimetría 2,06; media casi el triple de la mediana). Con ln(PIB) la distribución se vuelve simétrica (asimetría 0,04). La esperanza de vida tiene poca dispersión (CV = 10,2 %).</p><div class="pie">Estadística II · UCV</div></div>""")
S.append(f"""<div class="s"><h2>3. Diagrama de dispersión: PIB en escala original</h2><div class="dos"><img src="{img('figuras/fig03_dispersion_lineal.png')}" style="width:100%">
<div><p>Relación positiva pero <b>curva</b>: sube rápido hasta unos 20.000 US$ y luego se aplana.</p><br><p>Modelo 1: r = {f(L['r'],3)}, R² = {f(L['r2'],3)}</p><br><p>La recta no sigue la forma de la nube.</p></div></div><div class="pie">Estadística II · UCV</div></div>""")
S.append(f"""<div class="s"><h2>3. Diagrama de dispersión: ln(PIB)</h2><div class="dos"><img src="{img('figuras/fig04_dispersion_log.png')}" style="width:100%">
<div><p>Con el logaritmo la nube se vuelve una banda recta.</p><br><p><b>Modelo 2: r = {f(G['r'],3)}, R² = {f(G['r2'],3)}</b></p><br><p>Zonas azules por encima de la recta (salvo EE.&nbsp;UU.), zonas rojas por debajo. Venezuela, ligeramente por encima.</p></div></div><div class="pie">Estadística II · UCV</div></div>""")
filas = "".join(f"<tr><td>{k}</td><td>{'-' if np.isnan(v[1]) else f(v[1],3)}</td><td>{'DW ≈ 2: sí' if np.isnan(v[1]) else ('No se rechaza' if v[1]>=.05 else 'Se rechaza')}</td></tr>" for k, v in s2.items())
S.append(f"""<div class="s"><h2>4. Verificación de supuestos (Modelo 2)</h2><div class="dos"><table><tr><th>Prueba (H0: se cumple)</th><th>Valor p</th><th>H0 al 5 %</th></tr>{filas}</table>
<div><p>Normalidad aceptable (Lilliefors p = 0,26; Q-Q casi recto).</p><br><p>Heterocedasticidad leve: con errores robustos HC3, b sigue siendo muy significativa (t = {f(log.ols_hc3.tvalues[1],2)}).</p><br><p>En el Modelo 1 la prueba RESET rechaza la linealidad (p &lt; 0,001).</p></div></div><div class="pie">Estadística II · UCV</div></div>""")
S.append(f"""<div class="s"><h2>5 y 6. Ecuación estimada e interpretación</h2><div class="eq">Ŷ = {f(G['a'],4)} + {f(G['b'],4)} · ln(PIB per cápita)</div><ul>
<li><b>b = {f(G['b'],4)}:</b> +1 % de PIB → +{f(G['b']/100,4)} años; +10 % → +{f(G['b']*np.log(1.1),2)} años; <b>duplicar el PIB → +{f(G['b']*np.log(2),2)} años</b></li>
<li>El efecto depende del aumento relativo: rendimientos decrecientes del ingreso</li>
<li><b>a = {f(G['a'],2)}:</b> valor con PIB = 1 US$, fuera del rango observado; sin interpretación práctica</li>
<li>Error estándar de la estimación: s = {f(G['s'],3)} años (Modelo 1: {f(L['s'],3)})</li></ul><div class="pie">Estadística II · UCV</div></div>""")
S.append(f"""<div class="s"><h2>7, 9, 10 y 11. Inferencias (α = 0,05; gl = 98)</h2><table>
<tr><th>Prueba</th><th>Estadístico</th><th>Crítico</th><th>Valor p</th><th>IC 95 %</th></tr>
<tr><td>H0: B = 0</td><td>t = {f(G['t_b'],2)}</td><td>{f(G['tcrit'],4)}</td><td>&lt; 0,001</td><td>({f(G['ic_b'][0],3)} ; {f(G['ic_b'][1],3)})</td></tr>
<tr><td>H0: A = 0</td><td>t = {f(G['t_a'],2)}</td><td>{f(G['tcrit'],4)}</td><td>&lt; 0,001</td><td>({f(G['ic_a'][0],2)} ; {f(G['ic_a'][1],2)})</td></tr>
<tr><td>H0: ρ = 0</td><td>t = {f(G['t_r'],2)}</td><td>{f(G['tcrit'],4)}</td><td>&lt; 0,001</td><td>({f(G['ic_rho'][0],3)} ; {f(G['ic_rho'][1],3)})</td></tr>
<tr><td>ANOVA (H0: B = 0)</td><td>F = {f(G['F'],2)}</td><td>{f(G['Fcrit'],4)}</td><td>&lt; 0,001</td><td>F = t²</td></tr></table><br>
<div class="dos"><img src="{img('figuras/fig07_descomposicion.png')}" style="width:100%"><p><b>R² = {f(G['r2'],4)}</b>: el {f(100*G['r2'],1)} % de la variación de la esperanza de vida se explica por ln(PIB).</p></div><div class="pie">Estadística II · UCV</div></div>""")
S.append(f"""<div class="s"><h2>8. Intervalos para Venezuela (PIB pc = 4.244,5 US$)</h2><div class="eq">Ŷ0 = {f(G['a'],4)} + {f(G['b'],4)} × {f(iv['x0'],4)} = {f(iv['y0'],2)} años</div>
<table><tr><th>Intervalo al 95 %</th><th>Límite inferior</th><th>Límite superior</th></tr>
<tr><td>Media de Y en X0 (μy|x)</td><td>{f(iv['ic_media'][0],2)}</td><td>{f(iv['ic_media'][1],2)}</td></tr>
<tr><td>Valor particular (Ya)</td><td>{f(iv['ic_pred'][0],2)}</td><td>{f(iv['ic_pred'][1],2)}</td></tr></table><br>
<p>Valor observado de Venezuela: <b>72,67 años</b>, dentro del intervalo de predicción y 1,58 años por encima de lo que predice el modelo.</p><div class="pie">Estadística II · UCV</div></div>""")
S.append(f"""<div class="s"><h2>Conclusiones</h2><ul>
<li>Relación positiva, fuerte y significativa entre PIB per cápita y esperanza de vida (todas las pruebas con p &lt; 0,001)</li>
<li>La relación es logarítmica: el ingreso pesa mucho más en los países pobres que en los ricos</li>
<li>El modelo con ln(PIB) explica el 79 % de la variación, frente al 44 % del modelo lineal</li>
<li>El 21 % restante: salud pública, educación, conflictos, hábitos (zonas azules vs. zonas rojas)</li>
<li>Recomendación: PIB en PPA y regresión múltiple con gasto en salud y educación</li></ul><br>
<p style="font-size:14pt;color:#555">Datos, código y aplicación interactiva: github.com/allan230807/regresion-pib-esperanza-vida</p><div class="pie">Estadística II · UCV</div></div>""")

html = f"<!doctype html><html lang='es'><head><meta charset='utf-8'><style>{css}</style></head><body>{''.join(S)}</body></html>"
open("presentacion/diapositivas.html", "w", encoding="utf-8").write(html)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    import os
    exe = "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None
    b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"]); pg = b.new_page(); pg.set_content(html); pg.wait_for_timeout(500)
    pg.pdf(path=sys.argv[1] if len(sys.argv) > 1 else "presentacion/Respaldo_exposicion.pdf", width="13.333in", height="7.5in", print_background=True)
    b.close()
print("PDF listo")
