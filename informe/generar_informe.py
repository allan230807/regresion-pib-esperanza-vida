"""Genera el informe en Word (.docx) con python-docx.
Uso (desde la raíz del repositorio): python informe/generar_informe.py [salida.docx] [paginas.json]
"""
import sys, os, json, re
sys.path.insert(0, "src")
import numpy as np
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from regresion import cargar_datos, modelos, descriptivas

SALIDA = sys.argv[1] if len(sys.argv) > 1 else "informe/Informe_Regresion_PIB_Esperanza_de_Vida_v3.docx"
PAGINAS = json.load(open(sys.argv[2])) if len(sys.argv) > 2 and os.path.exists(sys.argv[2]) else {}

df = cargar_datos()
lin, log = modelos(df)
L, G = lin.res, log.res
FUENTE = "Times New Roman"


# ---------------- formato de números en español ----------------
def f(x, d=2):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def fp(p):
    return "< 0,001" if p < 0.001 else f(p, 3)

def fe(x, d=6):
    return f(x, d)


# ---------------- documento y estilos ----------------
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
sec.left_margin = Cm(3); sec.right_margin = Cm(2.5); sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)

st = doc.styles["Normal"]
st.font.name = FUENTE; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.5

for nombre, tam, antes in [("Heading 1", 14, 18), ("Heading 2", 12, 12)]:
    h = doc.styles[nombre]
    h.font.name = FUENTE; h.font.size = Pt(tam); h.font.bold = True; h.font.italic = False
    h.font.color.rgb = RGBColor(0, 0, 0)
    rpr = h.element.get_or_add_rPr(); rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), FUENTE)
    h.paragraph_format.space_before = Pt(antes); h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True; h.paragraph_format.line_spacing = 1.15

# pie de página con número
def campo_pagina(par):
    r = par.add_run()
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tag)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
        r._r.append(e)

sec.different_first_page_header_footer = True
fp_par = sec.footer.paragraphs[0]; fp_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
campo_pagina(fp_par)


SUB = re.compile(r"_([A-Za-z0-9Ŷ|]+)")

def corridas(p, texto, negrita=False, cursiva=False, tam=None):
    """Agrega el texto al párrafo convirtiendo _xx en subíndice (s_yx, S_Ŷ0, t_b)."""
    pos = 0
    for m in SUB.finditer(texto):
        if m.start() > pos:
            r = p.add_run(texto[pos:m.start()]); r.bold = negrita; r.italic = cursiva
            if tam: r.font.size = Pt(tam)
        r = p.add_run(m.group(1)); r.bold = negrita; r.italic = cursiva; r.font.subscript = True
        if tam: r.font.size = Pt(tam)
        pos = m.end()
    if pos < len(texto):
        r = p.add_run(texto[pos:]); r.bold = negrita; r.italic = cursiva
        if tam: r.font.size = Pt(tam)

def P(texto, alin="j", negrita=False, cursiva=False, tam=None, antes=None, despues=None, sangria=True):
    p = doc.add_paragraph()
    p.alignment = {"j": WD_ALIGN_PARAGRAPH.JUSTIFY, "c": WD_ALIGN_PARAGRAPH.CENTER,
                   "l": WD_ALIGN_PARAGRAPH.LEFT, "r": WD_ALIGN_PARAGRAPH.RIGHT}[alin]
    if alin == "j" and sangria:
        p.paragraph_format.first_line_indent = Cm(1.25)
    corridas(p, texto, negrita, cursiva, tam)
    if antes is not None: p.paragraph_format.space_before = Pt(antes)
    if despues is not None: p.paragraph_format.space_after = Pt(despues)
    return p

def PR(partes, alin="j"):
    """Párrafo con partes [(texto, 'b'|'i'|'')]."""
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if alin == "j" else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(1.25)
    for t, s in partes:
        corridas(p, t, "b" in s, "i" in s)
    return p

def EQ(texto):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(6)
    corridas(p, texto, cursiva=True)
    return p

def VIÑETA(texto):
    p = doc.add_paragraph(style="List Bullet"); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5; corridas(p, texto)
    return p

def H1(t):
    return doc.add_heading(t, level=1)

def H2(t):
    return doc.add_heading(t, level=2)

def salto():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

n_tab = [0]; n_fig = [0]

def leyenda(tipo, titulo):
    if tipo == "Tabla":
        n_tab[0] += 1; n = n_tab[0]
    else:
        n_fig[0] += 1; n = n_fig[0]
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True; p.paragraph_format.line_spacing = 1.0
    r = p.add_run(f"{tipo} {n}. "); r.bold = True; r.font.size = Pt(11)
    r = p.add_run(titulo); r.font.size = Pt(11)
    return n

def nota(t="Fuente: elaboración propia con datos del Banco Mundial (2026), Indicadores del Desarrollo Mundial."):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0; p.paragraph_format.space_after = Pt(10)
    r = p.add_run(t); r.font.size = Pt(9.5); r.italic = True

def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), color); tcPr.append(sh)

def TABLA(titulo, encabezado, filas, anchos, fuente_nota=None, tam=10, alinear_num=True, junta=True):
    leyenda("Tabla", titulo)
    t = doc.add_table(rows=1, cols=len(encabezado)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(encabezado):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(tam)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER; sombrear(c, "D9E2F3")
    for fila in filas:
        cs = t.add_row().cells
        for i, v in enumerate(fila):
            cs[i].text = ""
            par = cs[i].paragraphs[0]
            negr = isinstance(v, tuple)
            if negr: v = v[0]
            r = par.add_run(str(v)); r.font.size = Pt(tam); r.bold = negr
            par.alignment = WD_ALIGN_PARAGRAPH.LEFT if (i == 0 or not alinear_num) else WD_ALIGN_PARAGRAPH.CENTER
    for row in t.rows:
        for i, w in enumerate(anchos):
            row.cells[i].width = Cm(w)
            for par in row.cells[i].paragraphs:
                par.paragraph_format.line_spacing = 1.0; par.paragraph_format.space_after = Pt(1)
                par.paragraph_format.first_line_indent = None
    if junta:  # que la tabla no se parta entre páginas
        for row in t.rows[:-1]:
            for c in row.cells:
                for par in c.paragraphs: par.paragraph_format.keep_with_next = True
    # repetir encabezado en tablas largas
    trPr = t.rows[0]._tr.get_or_add_trPr(); e = OxmlElement("w:tblHeader"); e.set(qn("w:val"), "true"); trPr.append(e)
    nota(fuente_nota) if fuente_nota is not False else None
    return t

def sp(x, d=3):
    """Formato tipo SPSS en español: coma decimal y sin cero a la izquierda (,888)."""
    t = f(x, d)
    if t.startswith("0,"): t = t[1:]
    if t.startswith("-0,"): t = "-" + t[2:]
    return t

def sig(p):
    return sp(p, 3)

def TABLA_SPSS(titulo, encabezado, filas, anchos, notas, tam=9.5, izq=2):
    """encabezado: lista de filas; cada celda es (texto, colspan, rowspan); None = celda ocupada."""
    leyenda("Tabla", titulo)
    ncol = len(anchos); nh = len(encabezado)
    t = doc.add_table(rows=nh + len(filas), cols=ncol); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    tblPr = t._tbl.tblPr; lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    for j, w in enumerate(anchos): t.columns[j].width = Cm(w)
    ocupado = set()
    for i, fila in enumerate(encabezado):
        j = 0
        for celda in fila:
            while (i, j) in ocupado: j += 1
            texto, cs, rs = celda
            a = t.cell(i, j); b = t.cell(i + rs - 1, j + cs - 1)
            if (cs, rs) != (1, 1): a = a.merge(b)
            for di in range(rs):
                for dj in range(cs): ocupado.add((i + di, j + dj))
            a.text = ""; r = a.paragraphs[0].add_run(texto); r.bold = True; r.font.size = Pt(tam)
            a.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER; sombrear(a, "D9E2F3")
            j += cs
    for k, fila in enumerate(filas):
        for j, v in enumerate(fila):
            if v is None: continue
            c = t.cell(nh + k, j); c.text = ""
            r = c.paragraphs[0].add_run(str(v)); r.font.size = Pt(tam)
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT if j < izq else WD_ALIGN_PARAGRAPH.RIGHT
    for row in t.rows:
        for j, w in enumerate(anchos):
            row.cells[j].width = Cm(w)
            for par in row.cells[j].paragraphs:
                par.paragraph_format.line_spacing = 1.0; par.paragraph_format.space_after = Pt(1)
                par.paragraph_format.first_line_indent = None
    for k_, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr(); cs_ = OxmlElement("w:cantSplit"); cs_.set(qn("w:val"), "true"); trPr.append(cs_)
        if k_ < nh:
            th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
        if k_ < len(t.rows) - 1:
            for c in row.cells:
                for par in c.paragraphs: par.paragraph_format.keep_with_next = True
    for k, nt in enumerate(notas):
        p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(10 if k == len(notas) - 1 else 0)
        r = p.add_run(nt); r.font.size = Pt(9.5); r.italic = True
    return t

DEP = "Variable dependiente: Esperanza de vida al nacer 2024 (años)"
PRED = {False: "Variables predictoras: (Constante), PIB per cápita 2024 (US$)",
        True: "Variables predictoras: (Constante), ln(PIB per cápita)"}
NOMX = {False: "PIB per cápita (US$)", True: "ln(PIB per cápita)"}

def tabla_coef(m, titulo):
    r = m.res; bf = (lambda x: fe(x, 6)) if not m.log else (lambda x: f(x, 3))
    TABLA_SPSS(titulo,
        [[("Modelo", 2, 2), ("Coeficientes no estandarizados", 2, 1), ("Coeficientes estandarizados", 1, 1),
          ("t", 1, 2), ("Sig.", 1, 2), ("95,0 % intervalo de confianza para B", 2, 1)],
         [("B", 1, 1), ("Error estándar", 1, 1), ("Beta", 1, 1), ("Límite inferior", 1, 1), ("Límite superior", 1, 1)]],
        [["1", "(Constante)", f(r["a"], 3), f(r["se_a"], 3), "", f(r["t_a"], 3), sig(r["p_a"]), f(r["ic_a"][0], 3), f(r["ic_a"][1], 3)],
         ["", NOMX[m.log], bf(r["b"]), bf(r["se_b"]), sp(r["r"], 3), f(r["t_b"], 3), sig(r["p_b"]), bf(r["ic_b"][0]), bf(r["ic_b"][1])]],
        [1.1, 2.7, 1.8, 1.7, 2.5, 1.5, 1.1, 1.85, 1.85], ["a. " + DEP], tam=9)

def tabla_resumen(m, titulo):
    r = m.res; dw = m.supuestos()["Durbin-Watson (independencia)"][0]
    TABLA_SPSS(titulo,
        [[("Modelo", 1, 1), ("R", 1, 1), ("R cuadrado", 1, 1), ("R cuadrado corregido", 1, 1),
          ("Error típ. de la estimación", 1, 1), ("Durbin-Watson", 1, 1)]],
        [["1", sp(r["r"], 3) + "ᵃ", sp(r["r2"], 3), sp(r["r2_aj"], 3), f(r["s"], 4), f(dw, 3)]],
        [1.6, 2.0, 2.4, 2.8, 3.2, 2.6], ["a. " + PRED[m.log], "b. " + DEP], izq=1)

def tabla_anova_spss(m, titulo):
    r = m.res
    TABLA_SPSS(titulo,
        [[("Modelo", 2, 1), ("Suma de cuadrados", 1, 1), ("gl", 1, 1), ("Media cuadrática", 1, 1), ("F", 1, 1), ("Sig.", 1, 1)]],
        [["1", "Regresión", f(r["scr"], 3), "1", f(r["scr"], 3), f(r["F"], 3), sig(r["p_F"]) + "ᵇ"],
         ["", "Residual", f(r["sce"], 3), str(r["gl"]), f(r["s2"], 3), "", ""],
         ["", "Total", f(r["sct"], 3), str(r["n"] - 1), "", "", ""]],
        [1.3, 2.6, 2.9, 1.2, 2.9, 2.0, 1.7], ["a. " + DEP, "b. " + PRED[m.log]])

def FIG(ruta, titulo, ancho=15.5, fuente_nota=None):
    leyenda("Gráfico", titulo)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(ruta, width=Cm(ancho))
    nota(fuente_nota)


# ======================= PORTADA =======================
for linea in ["UNIVERSIDAD CENTRAL DE VENEZUELA", "FACULTAD DE CIENCIAS ECONÓMICAS Y SOCIALES",
              "ESCUELA DE ESTADÍSTICA Y CIENCIAS ACTUARIALES", "ESTADÍSTICA II"]:
    P(linea, "c", negrita=True, despues=0, antes=0).paragraph_format.line_spacing = 1.15
for _ in range(4): P("", "c", despues=0)
P("REGRESIÓN LINEAL BIVARIANTE:", "c", negrita=True, tam=16, despues=0)
P("PIB PER CÁPITA Y ESPERANZA DE VIDA AL NACER EN 100 PAÍSES (2024)", "c", negrita=True, tam=14)
for _ in range(3): P("", "c", despues=0)
P("Autores:", "r", negrita=True, despues=0)
P("Allan Arcia", "r", despues=0); P("Eddie Palomino", "r", despues=10)
P("Profesoras:", "r", negrita=True, despues=0)
P("Prof. Sandra Pinto", "r", despues=0); P("Prof. Yuraisi Capriles", "r", despues=0)
for _ in range(3): P("", "c", despues=0)
P("Caracas, noviembre de 2026", "c")
salto()

# ======================= ÍNDICE =======================
P("ÍNDICE", "c", negrita=True, tam=14, despues=12)
ENTRADAS = [
    (0, "Introducción"),
    (0, "I. Marco teórico"),
    (1, "1.1 Marco legal"),
    (1, "1.2 Marco metódico"),
    (0, "II. Desarrollo empírico"),
    (1, "1. Datos"),
    (1, "2. Estadísticas descriptivas y análisis"),
    (1, "3. Diagrama de dispersión y análisis"),
    (1, "4. Verificación de supuestos"),
    (1, "5. Estimación de los coeficientes y ecuación de regresión"),
    (1, "6. Interpretación de a y b"),
    (1, "7. Inferencias sobre A y B poblacionales"),
    (1, "8. Intervalo para la recta μy|x y para un valor particular Ya"),
    (1, "9. Inferencias sobre el coeficiente de correlación poblacional"),
    (1, "10. Coeficiente de determinación"),
    (1, "11. Análisis de varianza (ANOVA)"),
    (0, "Conclusiones y recomendaciones"),
    (0, "Bibliografía"),
    (0, "Anexo. Base de datos de los 100 países"),
]
ancho_texto = sec.page_width - sec.left_margin - sec.right_margin
for nivel, texto in ENTRADAS:
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(0.8 * nivel)
    p.paragraph_format.tab_stops.add_tab_stop(ancho_texto, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    r = p.add_run(texto); r.bold = nivel == 0
    p.add_run("\t" + str(PAGINAS.get(texto, "")))
salto()

# ======================= INTRODUCCIÓN =======================
H1("Introducción")
P("Una de las ideas más repetidas en economía y en salud pública es que los países más ricos viven más. "
  "En este trabajo quisimos comprobar esa idea con herramientas de Estadística II: tomamos 100 países del mundo y "
  "estudiamos si el producto interno bruto (PIB) por habitante sirve para explicar y predecir la esperanza de vida al nacer. "
  "La pregunta parece obvia, pero responderla bien exige medir qué tan fuerte es la relación, si es lineal, si se cumplen "
  "los supuestos del modelo y qué tan precisas son las predicciones que se pueden hacer con él.")
P("La muestra incluye a Venezuela, a los países donde se ubican las llamadas \"zonas azules\" (Japón, Italia, Grecia, "
  "Costa Rica y Estados Unidos, por la comunidad de Loma Linda en California), que son regiones famosas por la longevidad "
  "de su población, y a un grupo que llamamos \"zonas rojas\": diez países africanos con las esperanzas de vida más bajas "
  "del mundo, varios de ellos afectados por conflictos armados o crisis sanitarias (Nigeria, Chad, República Centroafricana, "
  "Lesoto, Somalia, Malí, Guinea, Benín, Níger y Sierra Leona). El resto de la muestra se escogió para cubrir todas las "
  "regiones y los cuatro niveles de ingreso que usa el Banco Mundial.")
P("La variable independiente (X) es el PIB per cápita de 2024 en dólares corrientes y la variable dependiente (Y) es la "
  "esperanza de vida al nacer de 2024, en años. Ambas provienen de los Indicadores del Desarrollo Mundial del Banco Mundial. "
  "Primero ajustamos el modelo con el PIB en su escala original; como veremos, la relación es claramente curva, así que el "
  "modelo principal usa el logaritmo natural del PIB per cápita, que es la forma habitual de trabajar esta relación "
  "desde el trabajo de Preston (1975).")
P("El informe se organiza en dos partes. En el marco teórico presentamos el marco legal y el marco metódico, es decir, "
  "las fórmulas y supuestos del modelo de regresión lineal simple. En el desarrollo empírico seguimos los once puntos "
  "del guion: datos, descriptivas, diagrama de dispersión, supuestos, estimación, interpretación, inferencias sobre "
  "los parámetros, intervalos de confianza y de predicción, inferencia sobre la correlación, coeficiente de determinación "
  "y análisis de varianza. Al final presentamos las conclusiones y recomendaciones. El procesamiento de los datos, "
  "las pruebas de hipótesis y la estimación de los modelos se ejecutaron mediante el paquete estadístico IBM SPSS "
  "Statistics, empleando scripts complementarios para la generación de visualizaciones analíticas. Las tablas "
  "principales (Resumen del modelo, ANOVA y Coeficientes) se presentan con la estructura de salida de SPSS.")

# ======================= MARCO TEÓRICO =======================
H1("I. Marco teórico")
H2("1.1 Marco legal")
P("Aunque este es un trabajo de estadística, las dos variables que estudiamos tienen respaldo en normas nacionales "
  "e internacionales, y los datos que usamos se producen bajo reglas claras de difusión. Las principales son las siguientes.")
VIÑETA("Constitución de la República Bolivariana de Venezuela (1999). El artículo 83 establece que la salud es un derecho "
       "social fundamental y una obligación del Estado, que debe garantizarla como parte del derecho a la vida. El artículo 84 "
       "crea el sistema público nacional de salud y el artículo 299 señala que el régimen socioeconómico debe asegurar el "
       "desarrollo humano integral y una existencia digna. La esperanza de vida es, en la práctica, uno de los resultados "
       "que miden si esos derechos se cumplen.")
VIÑETA("Ley de la Función Pública de Estadística (2001). Regula el Sistema Estadístico Nacional y al Instituto Nacional de "
       "Estadística (INE), y establece que la información estadística oficial es de interés público y debe producirse con "
       "criterios técnicos de calidad y oportunidad. Las cifras de Venezuela que publica el Banco Mundial se nutren en parte "
       "de fuentes oficiales nacionales y de estimaciones de organismos internacionales cuando estas no están disponibles.")
VIÑETA("Declaración Universal de los Derechos Humanos (1948), artículo 25, que reconoce el derecho de toda persona a un "
       "nivel de vida adecuado que le asegure la salud y el bienestar.")
VIÑETA("Agenda 2030 para el Desarrollo Sostenible de las Naciones Unidas (2015). El Objetivo 3 busca garantizar una vida "
       "sana y promover el bienestar para todos en todas las edades, y el Objetivo 8 promueve el crecimiento económico "
       "sostenido. Nuestro estudio relaciona precisamente un indicador de cada objetivo.")
VIÑETA("Principios Fundamentales de las Estadísticas Oficiales, adoptados por la Asamblea General de las Naciones Unidas "
       "(resolución 68/261 de 2014), que piden imparcialidad, transparencia metodológica y acceso público a los datos.")
VIÑETA("Licencia de los datos. Los Indicadores del Desarrollo Mundial del Banco Mundial se publican bajo licencia Creative "
       "Commons Atribución 4.0 (CC BY 4.0), que permite usarlos y redistribuirlos citando la fuente, como hacemos en este "
       "informe y en el repositorio.")

H2("1.2 Marco metódico")
PR([("Modelo de regresión lineal simple. ", "b"),
    ("El análisis de regresión estudia cómo cambia el valor medio de una variable dependiente Y cuando cambia una variable "
     "independiente X. En la población se plantea el modelo", "")])
EQ("Yi = A + B·Xi + εi ,   i = 1, 2, ..., n")
P("donde A (o β0) es el intercepto poblacional, B (o β1) es la pendiente poblacional y εi es el error aleatorio, que recoge todo lo que "
  "afecta a Y y no está en X. La recta de regresión poblacional es μy|x = A + B·X, es decir, el valor esperado de Y para "
  "un valor dado de X. Como no conocemos A y B, los estimamos con una muestra y obtenemos la recta estimada Ŷ = a + b·X.")
PR([("Supuestos. ", "b"), ("Para que las inferencias (pruebas t, F e intervalos) sean válidas, el modelo clásico supone que: "
    "(1) la relación entre X y la media de Y es lineal; (2) los errores tienen media cero; (3) los errores tienen varianza "
    "constante σ² para todo X (homocedasticidad); (4) los errores son independientes entre sí; y (5) los errores siguen una "
    "distribución normal. En resumen, εi ~ N(0, σ²) independientes. X se trata como una variable fija o medida sin error.", "")])
PR([("Estimación por mínimos cuadrados ordinarios (MCO). ", "b"),
    ("Los estimadores a y b son los que minimizan la suma de los cuadrados de los residuos, Σ(Yi − Ŷi)². Definiendo "
     "Sxx = Σ(Xi − X̄)², Syy = Σ(Yi − Ȳ)² y Sxy = Σ(Xi − X̄)(Yi − Ȳ), se obtiene:", "")])
EQ("b = Sxy / Sxx          a = Ȳ − b·X̄")
P("La varianza del modelo, σ², se estima con el cuadrado medio del error (residual): s_yx² = CME = SCRes / (n − 2), "
  "con n − 2 grados de libertad (98 en nuestro caso), donde SCRes = Σ(Yi − Ŷi)² es la suma de cuadrados residual. "
  "Su raíz, s_yx, es el error estándar (error típico) de la estimación.")
PR([("Inferencias sobre A y B. ", "b"),
    ("Bajo los supuestos, los estadísticos (b − B)/s_b y (a − A)/s_a siguen una distribución t de Student con n − 2 grados "
     "de libertad, donde", "")])
EQ("s_b = s_yx / √Sxx          s_a = s_yx · √( 1/n + X̄² / Sxx )")
P("Con ellos se construyen los intervalos de confianza b ± t(α/2; n−2)·s_b y a ± t(α/2; n−2)·s_a, y se prueban las hipótesis "
  "H0: B = 0 (X no explica a Y) y H0: A = 0. Se rechaza H0 si |t calculado| > t crítico, o lo que es igual, si el valor p es menor que α.")
PR([("Intervalos para μy|x y para Ya. ", "b"),
    ("Para un valor X0, la estimación puntual es Ŷ0 = a + b·X0. El intervalo de confianza para la media de Y en X0 "
     "(un punto de la recta poblacional, E(Y|X0)) y el intervalo de predicción para un valor individual Ya usan los "
     "siguientes errores estándar:", "")])
EQ("S_Ŷ0 = s_yx · √( 1/n + (X0 − X̄)² / Sxx )          S_Ya = s_yx · √( 1 + 1/n + (X0 − X̄)² / Sxx )")
EQ("E(Y|X0) = μy|x0:   Ŷ0 ± t(α/2; n−2) · S_Ŷ0          Ya:   Ŷ0 ± t(α/2; n−2) · S_Ya")
P("El intervalo de predicción siempre es más ancho, porque además de la incertidumbre sobre la recta incluye la "
  "variabilidad propia de cada observación.")
PR([("Coeficiente de correlación. ", "b"),
    ("El coeficiente de correlación de Pearson r = Sxy / √(Sxx·Syy) mide la intensidad de la relación lineal y va de −1 a 1. "
     "Para probar H0: ρ = 0 se usa t = r·√(n − 2) / √(1 − r²), con n − 2 grados de libertad. Para construir un intervalo "
     "de confianza para ρ se usa la transformación z de Fisher, z = ½·ln[(1 + r)/(1 − r)], que es aproximadamente normal "
     "con error estándar 1/√(n − 3).", "")])
PR([("Coeficiente de determinación y ANOVA. ", "b"),
    ("La variación total de Y se descompone en SCT = SCReg + SCRes, donde SCT = Syy es la suma de cuadrados total, "
     "SCReg = Σ(Ŷi − Ȳ)² es la suma de cuadrados de la regresión y SCRes la residual. El coeficiente de determinación "
     "R² = SCReg / SCT indica la proporción de la variación de Y explicada por X; en regresión simple R² = r². "
     "La tabla ANOVA compara el cuadrado medio de la regresión con el residual mediante F = CMReg / CME, que bajo H0: B = 0 "
     "sigue una distribución F con 1 y n − 2 grados de libertad. En regresión simple se cumple que F = t² de la pendiente.", "")])
PR([("Pruebas de los supuestos. ", "b"),
    ("La normalidad de los residuos se verifica en primer lugar con la inspección del gráfico P-P normal de regresión "
     "de residuo tipificado y del histograma del residuo tipificado con curva normal; como pruebas de bondad de ajuste "
     "complementarias se usan Shapiro-Wilk, Kolmogorov-Smirnov con corrección de Lilliefors y Jarque-Bera. La homocedasticidad se verifica con el gráfico de dispersión del residuo tipificado (ZRESID) contra el "
     "pronóstico tipificado (ZPRED) y con las pruebas de Breusch-Pagan y de White. La linealidad se evalúa con el diagrama de "
     "dispersión y con la prueba RESET de Ramsey. La independencia se revisa con el estadístico de Durbin-Watson, que "
     "debe estar cerca de 2. En todas las pruebas la hipótesis nula es que el supuesto se cumple.", "")])
PR([("Transformación logarítmica. ", "b"),
    ("Cuando la nube de puntos muestra una curva que crece rápido y luego se aplana, una solución estándar es transformar "
     "X con el logaritmo natural. El modelo sigue siendo lineal en los parámetros, Y = A + B·ln(X) + ε, por lo que todas "
     "las fórmulas anteriores se aplican igual, reemplazando X por ln(X). La interpretación cambia: un aumento de 1 % en X "
     "se asocia con un cambio de aproximadamente B/100 unidades en Y. En la literatura sobre salud y desarrollo esta forma "
     "se conoce como curva de Preston (Preston, 1975).", "")])

# ======================= DESARROLLO EMPÍRICO =======================
H1("II. Desarrollo empírico")
H2("1. Datos")
P("Los datos se descargaron el 15 de noviembre de 2026 de la API de los Indicadores del Desarrollo Mundial del Banco "
  "Mundial. Usamos dos indicadores: NY.GDP.PCAP.CD, el PIB per cápita en dólares estadounidenses a precios corrientes, "
  "y SP.DYN.LE00.IN, la esperanza de vida al nacer en años para ambos sexos. Las dos variables salen de esa misma "
  "base de datos oficial para los 100 países, sin completar huecos con otras fuentes, de modo que todas las cifras son "
  "comparables entre sí. El Banco Mundial compila el PIB a partir de las cuentas nacionales de cada país y de la OCDE, y la "
  "esperanza de vida a partir de las Perspectivas de la Población Mundial de la División de Población de las Naciones Unidas. Trabajamos con el año 2024 porque es el "
  "más reciente que tiene ambos indicadores publicados para casi todos los países; los valores de 2025 todavía no "
  "estaban disponibles al momento de la descarga.")
P("La unidad de análisis es el país y la muestra tiene n = 100 países. Para armarla incluimos a Venezuela, a los cinco "
  "países de las zonas azules y a los diez países de las zonas rojas, y completamos con 84 países de todas las regiones. "
  "Sudán del Sur, que tiene una de las esperanzas de vida más bajas, quedó fuera porque el Banco Mundial no publica su "
  "PIB de 2024. Venezuela sí tiene dato de 2024 (US$ 4.244,5), aunque conviene recordar que sus cuentas nacionales "
  "tienen más incertidumbre que las de otros países por la escasa publicación de cifras oficiales en los últimos años. "
  "La Tabla 1 resume la composición de la muestra; la base completa está en el anexo.")
comp = df.groupby("region").agg(n=("pais", "count"), pib=("pib_pc_usd_2024", "mean"), ev=("esperanza_vida_2024", "mean")).sort_values("n", ascending=False)
TABLA("Composición de la muestra por región del Banco Mundial",
      ["Región", "Países", "PIB per cápita medio (US$)", "Esperanza de vida media (años)"],
      [[i, int(r.n), f(r.pib, 0), f(r.ev, 1)] for i, r in comp.iterrows()] + [[("Total",), ("100",), (f(df.pib_pc_usd_2024.mean(), 0),), (f(df.esperanza_vida_2024.mean(), 1),)]],
      [7.0, 2.0, 3.5, 3.5])

H2("2. Estadísticas descriptivas y análisis")
dX, dL, dY = (descriptivas(df[c]) for c in ["pib_pc_usd_2024", "ln_pib_pc", "esperanza_vida_2024"])
filas = []
for k in ["Media", "Mediana", "Desviación estándar", "Coef. de variación (%)", "Mínimo", "Q1", "Q3", "Máximo",
          "Rango", "Rango intercuartílico", "Asimetría", "Curtosis (exceso)"]:
    d = 2 if k in ("Asimetría", "Curtosis (exceso)", "Coef. de variación (%)") else None
    filas.append([k, f(dX[k], d if d else 1), f(dL[k], d if d else 3), f(dY[k], d if d else 2)])
TABLA("Estadísticas descriptivas de las variables (n = 100)",
      ["Estadístico", "PIB per cápita (US$)", "ln(PIB per cápita)", "Esperanza de vida (años)"], filas, [5.2, 3.8, 3.5, 3.8])
P(f"El PIB per cápita es una variable muy dispersa y asimétrica. La media ({f(dX['Media'],0)} dólares) casi triplica la "
  f"mediana ({f(dX['Mediana'],0)} dólares), el coeficiente de variación es de {f(dX['Coef. de variación (%)'],1)} % y la "
  f"asimetría es {f(dX['Asimetría'],2)}, es decir, hay muchos países con ingresos bajos y medios y unos pocos países muy ricos "
  f"que estiran la distribución hacia la derecha. El país más pobre de la muestra es Afganistán ({f(dX['Mínimo'],1)} dólares) "
  f"y el más rico es Luxemburgo ({f(dX['Máximo'],1)} dólares), una diferencia de más de 300 veces.")
P(f"Al aplicar el logaritmo natural la distribución cambia por completo: la media ({f(dL['Media'],3)}) y la mediana "
  f"({f(dL['Mediana'],3)}) casi coinciden, la asimetría baja a {f(dL['Asimetría'],2)} y el coeficiente de variación a "
  f"{f(dL['Coef. de variación (%)'],1)} %. Esto ya sugiere que ln(PIB) es una escala más adecuada para el análisis.")
P(f"La esperanza de vida es mucho menos dispersa (coeficiente de variación de {f(dY['Coef. de variación (%)'],1)} %). "
  f"Su media es {f(dY['Media'],2)} años y su mediana {f(dY['Mediana'],2)} años, con una ligera asimetría negativa "
  f"({f(dY['Asimetría'],2)}): la mayoría de los países está entre 68,6 y 79,2 años (Q1 y Q3), y la cola izquierda la "
  f"forman los países de las zonas rojas. El mínimo es Nigeria ({f(dY['Mínimo'],2)} años) y el máximo Suiza "
  f"({f(dY['Máximo'],2)} años), casi 30 años de diferencia.")
FIG("figuras/fig01_histogramas.png", "Histogramas del PIB per cápita, su logaritmo y la esperanza de vida", 16)
ing = df.groupby("ingreso").agg(n=("pais", "count"), pib=("pib_pc_usd_2024", "mean"), ev=("esperanza_vida_2024", "mean"), evmin=("esperanza_vida_2024", "min"), evmax=("esperanza_vida_2024", "max"))
ing = ing.loc[["Ingreso bajo", "Ingreso mediano bajo", "Ingreso mediano alto", "Ingreso alto"]]
TABLA("Esperanza de vida según el nivel de ingreso del Banco Mundial",
      ["Nivel de ingreso", "Países", "PIB pc medio (US$)", "Esp. de vida media", "Mínimo", "Máximo"],
      [[i, int(r.n), f(r.pib, 0), f(r.ev, 1), f(r.evmin, 1), f(r.evmax, 1)] for i, r in ing.iterrows()], [4.6, 1.7, 3.0, 2.8, 2.0, 2.0])
P("La Tabla 3 y el Gráfico 2 muestran el patrón que vamos a modelar: la esperanza de vida media sube de 62,5 años en los "
  "países de ingreso bajo a 81,0 años en los de ingreso alto. Pero el salto no es proporcional al dinero. Pasar de ingreso "
  "bajo a mediano bajo (unos 1.600 dólares más por persona) se asocia con 5,5 años más de vida, mientras que pasar de "
  "ingreso mediano alto a alto (unos 41.700 dólares más) se asocia con 6,4 años. Este rendimiento decreciente es justamente "
  "lo que captura el logaritmo.")
FIG("figuras/fig02_boxplots_ingreso.png", "Diagramas de caja del PIB per cápita y de la esperanza de vida por nivel de ingreso", 16)
grp = df.groupby("grupo").agg(n=("pais", "count"), pib=("pib_pc_usd_2024", "mean"), ev=("esperanza_vida_2024", "mean")).loc[["Zona azul", "Zona roja", "Venezuela", "Otro"]]
TABLA("Comparación de los grupos de interés",
      ["Grupo", "Países", "PIB per cápita medio (US$)", "Esperanza de vida media (años)"],
      [["Zonas azules" if i == "Zona azul" else "Zonas rojas" if i == "Zona roja" else "Resto de países" if i == "Otro" else i, int(r.n), f(r.pib, 0), f(r.ev, 2)] for i, r in grp.iterrows()],
      [5.5, 2.0, 4.2, 4.2])
P("Las diferencias entre los grupos son enormes. Los cinco países de zonas azules tienen en promedio 40.775 dólares por "
  "persona y 81,9 años de esperanza de vida, mientras que los diez de zonas rojas apenas superan los 1.000 dólares y viven en "
  "promedio 59,0 años, casi 23 años menos. Venezuela queda en una posición intermedia: con 4.244,5 dólares por persona, "
  "su esperanza de vida es de 72,7 años, un poco por debajo del promedio de la muestra.")

H2("3. Diagrama de dispersión y análisis")
P("El Gráfico 3 muestra la nube de puntos con el PIB per cápita en su escala original junto con la recta de mínimos "
  "cuadrados del Modelo 1. Se ve una relación positiva clara, pero no lineal: entre 0 y 20.000 dólares la esperanza de vida "
  "sube muy rápido, y a partir de allí la nube se aplana alrededor de 80 a 85 años. La recta pasa por encima de casi todos "
  "los países pobres de la izquierda, por debajo de los países de ingreso medio alto y vuelve a pasar por encima de los "
  "países más ricos. Es el patrón típico de un modelo mal especificado.")
FIG("figuras/fig03_dispersion_lineal.png", "Diagrama de dispersión con el PIB per cápita en escala original (Modelo 1)", 15.5)
P("Cuando ponemos el PIB en escala logarítmica (Gráfico 4) la nube se convierte en una banda bastante recta y la recta "
  f"del Modelo 2 la sigue bien en todo el rango. La correlación lineal pasa de r = {f(L['r'],4)} con el PIB en bruto a "
  f"r = {f(G['r'],4)} con ln(PIB). Como referencia, la correlación por rangos de Spearman, que no depende de la "
  "escala, es 0,9036, lo que confirma que la relación es monótona y fuerte y que el problema del Modelo 1 era la forma, "
  "no la intensidad.")
FIG("figuras/fig04_dispersion_log.png", "Diagrama de dispersión con el PIB per cápita en escala logarítmica y recta del Modelo 2", 15.5)
P("En el gráfico también se ven casos interesantes. Los países de zonas azules están por encima de la recta, salvo "
  "Estados Unidos, que vive unos 5,6 años menos de lo que predice el modelo para su ingreso; esto tiene sentido, porque la "
  "zona azul es una comunidad pequeña (Loma Linda) y no representa al país completo. Las zonas rojas quedan todas por "
  "debajo de la recta, sobre todo Nigeria y Chad, que viven unos 10 años menos de lo esperado. Venezuela está ligeramente "
  "por encima de la recta. Otro caso que llama la atención es Guyana, que tiene un PIB per cápita de casi 30.000 dólares por "
  "el reciente auge petrolero pero una esperanza de vida de 70,3 años, porque ese ingreso todavía no se ha traducido en "
  "mejores condiciones de salud.")

H2("4. Verificación de supuestos")
P("Verificamos los supuestos sobre los residuos de los dos modelos con las pruebas descritas en el marco metódico, "
  "usando un nivel de significación α = 0,05. La Tabla 5 resume los resultados.")
s1, s2 = lin.supuestos(), log.supuestos()
def decision(k, p):
    if np.isnan(p):
        return "Cerca de 2: no hay autocorrelación"
    return "No se rechaza H0" if p >= 0.05 else "Se rechaza H0"
filas = []
for k in s1:
    e1, p1 = s1[k]; e2, p2 = s2[k]
    filas.append([k, f(e1, 3), "-" if np.isnan(p1) else fp(p1), "-" if np.isnan(p2) else f(e2, 3), "-" if np.isnan(p2) else fp(p2)])
filas[-1][3] = f(s2["Durbin-Watson (independencia)"][0], 3)
TABLA("Pruebas de los supuestos del modelo sobre los residuos",
      ["Prueba", "Modelo 1 estadístico", "Modelo 1 valor p", "Modelo 2 estadístico", "Modelo 2 valor p"], filas, [6.0, 2.6, 2.3, 2.6, 2.3], tam=9.5)
FIG("figuras/fig05_residuos_lineal.png", "Gráfico P-P normal, histograma con curva normal y ZPRED vs ZRESID del Modelo 1 (PIB en escala original)", 16)
P("En el Modelo 1 el problema principal es la linealidad. La prueba RESET rechaza con mucha fuerza la hipótesis de que "
  "la forma lineal es correcta (p < 0,001) y en los residuos se ve una curva: residuos negativos "
  "en los extremos y positivos en el centro, visible en el gráfico ZPRED vs ZRESID. Además, las tres pruebas de normalidad rechazan H0 y la prueba de White "
  "detecta heterocedasticidad. Por eso no es recomendable usar el Modelo 1 para hacer inferencias ni predicciones.")
FIG("figuras/fig06_residuos_log.png", "Gráfico P-P normal, histograma con curva normal y ZPRED vs ZRESID del Modelo 2 (ln del PIB)", 16)
P("En el Modelo 2 la situación mejora mucho. El gráfico ZPRED vs ZRESID ya no muestra una curva marcada y el estadístico "
  "RESET baja de 44,6 a 6,2. Sobre cada supuesto concluimos lo siguiente:")
VIÑETA("Linealidad: la relación entre ln(PIB) y la esperanza de vida es aproximadamente lineal, como se ve en el Gráfico 4. "
       "La prueba RESET todavía da p = 0,014, lo que indica una curvatura leve en los extremos que no cambia las conclusiones.")
VIÑETA("Normalidad: en el gráfico P-P normal de regresión de residuo tipificado los puntos siguen de cerca la diagonal, y el "
       "histograma del residuo tipificado con curva normal (media 0, desviación típica 0,995) tiene forma aproximadamente "
       "acampanada; la única desviación visible viene de pocos países en la cola izquierda (Nigeria, Chad y Guyana, con "
       "residuos tipificados cercanos a −3). Como pruebas de bondad de ajuste complementarias, Lilliefors no rechaza la "
       "normalidad (p = 0,261), mientras que Shapiro-Wilk (p = 0,030) y Jarque-Bera (p = 0,044) la rechazan al 5 % pero no al 1 %. Con n = 100, el teorema central "
       "del límite garantiza que los estimadores a y b tienen distribución aproximadamente normal, así que las pruebas t y F son "
       "confiables.")
VIÑETA("Homocedasticidad: Breusch-Pagan (p = 0,005) y White (p = 0,014) detectan heterocedasticidad. En el gráfico ZPRED vs ZRESID se nota "
       "que la dispersión de los residuos es algo mayor en los países de ingreso bajo y medio que en los ricos, cuyos valores "
       "se concentran entre 80 y 85 años. Para comprobar que esto no afecta las conclusiones recalculamos los errores estándar "
       f"con el método robusto HC3 de White: el error estándar de b pasa de {f(G['se_b'],4)} a {f(log.ols_hc3.bse[1],4)} y "
       f"el estadístico t de {f(G['t_b'],2)} a {f(log.ols_hc3.tvalues[1],2)}, de modo que b sigue siendo altamente significativa.")
VIÑETA(f"Independencia: los datos son de corte transversal (un dato por país), así que no hay orden temporal. El estadístico "
       f"de Durbin-Watson, que se reporta en la tabla Resumen del modelo, es {f(s2['Durbin-Watson (independencia)'][0],3)}. "
       "Como está muy cerca de 2 (y dentro del intervalo habitual de 1,5 a 2,5), no hay indicios de autocorrelación de los residuos.")
P("En conclusión, el Modelo 2 cumple razonablemente los supuestos y es claramente superior al Modelo 1. A partir de aquí "
  "lo usamos como modelo principal; en los puntos 5, 10 y 11 mostramos también los resultados del Modelo 1 para comparar.")

H2("5. Estimación de los coeficientes y ecuación de regresión")
P("Con las sumas de cuadrados de la muestra calculamos los estimadores de mínimos cuadrados. La Tabla 6 muestra los "
  "insumos de los dos modelos.")
TABLA("Insumos para la estimación por mínimos cuadrados",
      ["Cantidad", "Modelo 1 (X = PIB)", "Modelo 2 (X = ln PIB)"],
      [["n", "100", "100"], ["X̄", f(L["xm"], 3), f(G["xm"], 4)], ["Ȳ", f(L["ym"], 4), f(G["ym"], 4)],
       ["Sxx", f(L["sxx"], 1), f(G["sxx"], 4)], ["Sxy", f(L["sxy"], 2), f(G["sxy"], 4)], ["Syy", f(L["sct"], 4), f(G["sct"], 4)]],
      [4.0, 5.5, 5.5])
P(f"Para el Modelo 2: b = Sxy / Sxx = {f(G['sxy'],4)} / {f(G['sxx'],4)} = {f(G['b'],4)}, y "
  f"a = Ȳ − b·X̄ = {f(G['ym'],4)} − {f(G['b'],4)} × {f(G['xm'],4)} = {f(G['a'],4)}. Las ecuaciones estimadas son:", sangria=False)
EQ(f"Modelo 1:   Ŷ = {f(L['a'],4)} + {fe(L['b'],6)} · PIB")
EQ(f"Modelo 2:   Ŷ = {f(G['a'],4)} + {f(G['b'],4)} · ln(PIB)")
P("Las tablas siguientes presentan los coeficientes con la estructura de salida de SPSS. En la fila (Constante) está "
  "el intercepto a y en la fila de la variable independiente la pendiente b; el coeficiente estandarizado Beta coincide "
  "con r en la regresión simple.", sangria=False)
tabla_coef(log, "Coeficientes(a) del Modelo 2: Y = a + b·ln(PIB)")
tabla_coef(lin, "Coeficientes(a) del Modelo 1: Y = a + b·PIB")
P(f"El error estándar de la estimación es s_yx = {f(L['s'],3)} años en el Modelo 1 y s_yx = {f(G['s'],3)} años en el Modelo 2. "
  "Es decir, con ln(PIB) las predicciones se equivocan en promedio casi 2,2 años menos.")

H2("6. Interpretación de a y b")
PR([("Modelo 2 (principal). ", "b"),
    (f"La pendiente b = {f(G['b'],4)} indica que, por cada unidad que aumenta ln(PIB per cápita), la esperanza de vida "
     f"aumenta en promedio {f(G['b'],2)} años. Como una unidad de logaritmo es difícil de imaginar, es más útil leerla en "
     f"porcentajes: un aumento de 1 % en el PIB per cápita se asocia con {f(G['b']/100,4)} años más de esperanza de vida "
     f"(unos 16 días), un aumento de 10 % se asocia con b·ln(1,1) = {f(G['b']*np.log(1.1),2)} años más, y duplicar el "
     f"PIB per cápita se asocia con b·ln(2) = {f(G['b']*np.log(2),2)} años más. Lo importante es que el efecto depende del "
     "aumento relativo y no del absoluto: sumar 1.000 dólares a un país de 1.000 dólares (duplicarlo) tiene el mismo efecto "
     "que sumar 50.000 dólares a un país de 50.000.", "")])
PR([("", ""), (f"El intercepto a = {f(G['a'],2)} sería la esperanza de vida esperada cuando ln(PIB) = 0, es decir, con un PIB "
     "per cápita de 1 dólar. Ese valor está muy lejos del rango observado (de 417 a 137.782 dólares), así que el intercepto "
     "no tiene una interpretación práctica; su función es ubicar la recta.", "")])
PR([("Modelo 1. ", "b"),
    (f"La pendiente b = {fe(L['b'],6)} dice que cada dólar adicional de PIB per cápita se asocia con {fe(L['b'],6)} años "
     f"más de vida, o sea, {f(L['b']*10000,2)} años por cada 10.000 dólares. El intercepto a = {f(L['a'],2)} años sería la "
     "esperanza de vida de un país con PIB igual a cero. Estas lecturas son engañosas porque suponen que el efecto de cada "
     "dólar es el mismo en Chad que en Suiza, cosa que los datos desmienten.", "")])

H2("7. Inferencias sobre A y B poblacionales")
P(f"Trabajamos con α = 0,05 y n − 2 = {G['gl']} grados de libertad, por lo que el valor crítico de la t de Student "
  f"para una prueba bilateral es t(0,025; 98) = {f(G['tcrit'],4)}. Los valores de b, s_b, t, Sig. y los límites del "
  "intervalo para B se leen en la tabla Coeficientes(a) del punto 5.")
PR([("Nota metodológica. ", "b"),
    (f"Como el tamaño muestral es grande (n = 100 > 30), la distribución t de Student con 98 grados de libertad converge "
     f"asintóticamente a la normal estándar Z: el valor crítico t(0,025; 98) = {f(G['tcrit'],4)} es prácticamente igual a "
     f"Z(0,975) = 1,96. Por eso el estadístico t que reporta la salida de SPSS es equivalente al contraste clásico Z de la "
     f"guía de teoría, y la decisión es la misma con cualquiera de los dos valores críticos (|t| = {f(G['t_b'],2)} supera "
     "con holgura a ambos).", "")])
PR([("Prueba sobre la pendiente B. ", "b"), ("H0: B = 0 (el PIB no influye en la esperanza de vida) contra H1: B ≠ 0.", "")])
EQ(f"t = b / s_b = {f(G['b'],4)} / {f(G['se_b'],4)} = {f(G['t_b'],2)}")
P(f"Como |t| = {f(G['t_b'],2)} > {f(G['tcrit'],4)} (valor p < 0,001), rechazamos H0. Hay evidencia muy fuerte de que la "
  "pendiente poblacional es distinta de cero, es decir, el logaritmo del PIB per cápita sí explica la esperanza de vida. "
  f"Además, como se verá en el punto 11, t_b² = {f(G['t_b'],4)}² = {f(G['t_b']**2,2)} = F de la tabla ANOVA, igualdad "
  "que siempre se cumple en la regresión simple.")
PR([("Prueba sobre el intercepto A. ", "b"), ("H0: A = 0 contra H1: A ≠ 0.", "")])
EQ(f"t = a / s_a = {f(G['a'],4)} / {f(G['se_a'],4)} = {f(G['t_a'],2)}")
P(f"Como |t| = {f(G['t_a'],2)} > {f(G['tcrit'],4)} (valor p < 0,001), también rechazamos H0: el intercepto poblacional es distinto de cero.")
PR([("Intervalos de confianza al 95 %. ", "b"), ("", "")])
EQ(f"B:  {f(G['b'],4)} ± {f(G['tcrit'],4)} × {f(G['se_b'],4)}  →  ({f(G['ic_b'][0],4)} ; {f(G['ic_b'][1],4)})")
EQ(f"A:  {f(G['a'],4)} ± {f(G['tcrit'],4)} × {f(G['se_a'],4)}  →  ({f(G['ic_a'][0],4)} ; {f(G['ic_a'][1],4)})")
P(f"Con 95 % de confianza, duplicar el PIB per cápita se asocia en la población con un aumento de entre "
  f"{f(G['ic_b'][0]*np.log(2),2)} y {f(G['ic_b'][1]*np.log(2),2)} años de esperanza de vida. Ninguno de los dos intervalos "
  "contiene el cero, lo que es coherente con las pruebas de hipótesis.")
hc = log.ols_hc3
TABLA("Inferencias sobre A y B (Modelo 2): errores estándar clásicos y robustos HC3",
      ["Parámetro", "Estimación", "Error est. clásico", "IC 95 % clásico", "Error est. HC3", "IC 95 % HC3"],
      [["A", f(G["a"], 4), f(G["se_a"], 4), f"({f(G['ic_a'][0],2)} ; {f(G['ic_a'][1],2)})", f(hc.bse[0], 4), f"({f(hc.conf_int()[0][0],2)} ; {f(hc.conf_int()[0][1],2)})"],
       ["B", f(G["b"], 4), f(G["se_b"], 4), f"({f(G['ic_b'][0],3)} ; {f(G['ic_b'][1],3)})", f(hc.bse[1], 4), f"({f(hc.conf_int()[1][0],3)} ; {f(hc.conf_int()[1][1],3)})"]],
      [2.0, 2.4, 2.6, 3.3, 2.4, 3.3], tam=9.5)
P("Como vimos en los supuestos, hay algo de heterocedasticidad, por eso la Tabla 9 compara los resultados con los "
  "errores robustos HC3. Los intervalos casi no cambian y las conclusiones son las mismas.")

H2("8. Intervalo para la recta μy|x y para un valor particular Ya")
v = df[df.pais == "Venezuela"].iloc[0]; iv = log.intervalos(v.pib_pc_usd_2024)
P(f"Aplicamos los intervalos al caso de Venezuela, con X0 = 4.244,5 dólares, es decir, ln(X0) = {f(iv['x0'],4)}. "
  "La estimación puntual es:", sangria=False)
EQ(f"Ŷ0 = {f(G['a'],4)} + {f(G['b'],4)} × {f(iv['x0'],4)} = {f(iv['y0'],2)} años")
P(f"Los errores estándar de la respuesta media E(Y|X0) y del valor individual Ya se obtienen con las fórmulas de la "
  f"cátedra, usando s_yx = {f(G['s'],4)}, n = 100, X̄ = {f(G['xm'],4)} y Sxx = {f(G['sxx'],4)}:", sangria=False)
EQ(f"S_Ŷ0 = s_yx·√( 1/n + (X0 − X̄)²/Sxx ) = {f(G['s'],4)} × √( 1/100 + ({f(iv['x0'],4)} − {f(G['xm'],4)})² / {f(G['sxx'],4)} ) = {f(iv['se_media'],4)}")
EQ(f"S_Ya = s_yx·√( 1 + 1/n + (X0 − X̄)²/Sxx ) = {f(G['s'],4)} × √( 1 + 1/100 + ({f(iv['x0'],4)} − {f(G['xm'],4)})² / {f(G['sxx'],4)} ) = {f(iv['se_pred'],4)}")
P(f"Con t(0,025; 98) = {f(G['tcrit'],4)}, los intervalos al 95 % son:", sangria=False)
EQ(f"IC 95 % para E(Y|X0) = μy|x0:   {f(iv['y0'],2)} ± {f(G['tcrit']*iv['se_media'],2)}  →  ({f(iv['ic_media'][0],2)} ; {f(iv['ic_media'][1],2)}) años")
EQ(f"IC 95 % para Ya:   {f(iv['y0'],2)} ± {f(G['tcrit']*iv['se_pred'],2)}  →  ({f(iv['ic_pred'][0],2)} ; {f(iv['ic_pred'][1],2)}) años")
P(f"Interpretación: con 95 % de confianza, la esperanza de vida media de todos los países con un PIB per cápita de "
  f"4.244,5 dólares está entre {f(iv['ic_media'][0],2)} y {f(iv['ic_media'][1],2)} años. Para un país en particular con "
  f"ese ingreso, como Venezuela, esperamos que su esperanza de vida esté entre {f(iv['ic_pred'][0],2)} y "
  f"{f(iv['ic_pred'][1],2)} años. El valor observado de Venezuela, {f(v.esperanza_vida_2024,2)} años, cae dentro del "
  f"intervalo de predicción y está {f(v.esperanza_vida_2024-iv['y0'],2)} años por encima de lo que predice el modelo.")
filas = []
for p_ in ["Venezuela", "Nigeria", "Costa Rica", "Japón", "Estados Unidos"]:
    x = df[df.pais == p_].iloc[0]; i_ = log.intervalos(x.pib_pc_usd_2024)
    filas.append([p_, f(x.pib_pc_usd_2024, 1), f(i_["y0"], 2), f"({f(i_['ic_media'][0],2)} ; {f(i_['ic_media'][1],2)})",
                  f"({f(i_['ic_pred'][0],2)} ; {f(i_['ic_pred'][1],2)})", f(x.esperanza_vida_2024, 2)])
TABLA("Estimaciones e intervalos al 95 % para Venezuela y países de contraste de ingresos bajos y altos (Modelo 2)",
      ["País", "PIB pc (US$)", "Ŷ0", "IC para E(Y|X0)", "IC para Ya", "Y observado"], filas, [3.0, 2.4, 1.6, 3.4, 3.4, 2.2], tam=9.5)
P("La Tabla 10 repite el cálculo para otros países de interés. Los intervalos para la media son estrechos porque, con "
  "100 países, la recta está bien estimada; los de predicción son más anchos, de unos ±7 años, porque además incluyen la "
  "variación propia de cada país. Los intervalos son más anchos lejos de X̄ (por ejemplo en Estados Unidos o Nigeria) que "
  "cerca de ella. Nigeria y Estados Unidos quedan por fuera o al borde de sus intervalos de predicción, lo que confirma que "
  "son casos atípicos: tienen menos esperanza de vida de la que su ingreso haría esperar.")

H2("9. Inferencias sobre el coeficiente de correlación poblacional")
P(f"El coeficiente de correlación muestral entre ln(PIB) y la esperanza de vida es r = {f(G['r'],4)}, una correlación "
  "positiva y fuerte. Para saber si es significativa planteamos H0: ρ = 0 contra H1: ρ ≠ 0, con α = 0,05.")
EQ(f"t = r·√(n − 2) / √(1 − r²) = {f(G['r'],4)} × √98 / √(1 − {f(G['r2'],4)}) = {f(G['t_r'],2)}")
P(f"Como {f(G['t_r'],2)} > {f(G['tcrit'],4)} (valor p < 0,001), rechazamos H0: existe una correlación lineal "
  "significativa entre las variables en la población. Este estadístico es exactamente igual al t de la pendiente, como "
  "debe ocurrir en regresión simple, y por lo tanto también se cumple t² = F del ANOVA. Al igual que en el punto 7, con "
  f"n = 100 > 30 la t con 98 grados de libertad es prácticamente una normal estándar, de modo que comparar con "
  f"t(0,025; 98) = {f(G['tcrit'],4)} o con Z(0,975) = 1,96 lleva a la misma decisión.")
P(f"Para el intervalo de confianza usamos la transformación de Fisher: z = ½·ln[(1 + r)/(1 − r)] = {f(G['z_fisher'],4)}, "
  f"con error estándar 1/√97 = {f(1/np.sqrt(97),4)}. El intervalo para z es {f(G['z_fisher'],4)} ± 1,96 × "
  f"{f(1/np.sqrt(97),4)} y, devolviéndolo a la escala de r con la tangente hiperbólica, obtenemos:", sangria=False)
EQ(f"IC 95 % para ρ:  ({f(G['ic_rho'][0],4)} ; {f(G['ic_rho'][1],4)})")
P(f"Con 95 % de confianza, la correlación poblacional está entre {f(G['ic_rho'][0],2)} y {f(G['ic_rho'][1],2)}. Para el "
  f"Modelo 1 la correlación es r = {f(L['r'],4)}, también significativa (t = {f(L['t_r'],2)}), con intervalo "
  f"({f(L['ic_rho'][0],4)} ; {f(L['ic_rho'][1],4)}); los dos intervalos no se solapan, lo que muestra que la relación lineal "
  "es bastante más fuerte en escala logarítmica.")

H2("10. Coeficiente de determinación")
tabla_resumen(log, "Resumen del modelo(b) del Modelo 2")
EQ(f"R² = SCReg / SCT = {f(G['scr'],2)} / {f(G['sct'],2)} = {f(G['r2'],4)}")
P(f"El {f(100*G['r2'],1)} % de la variación de la esperanza de vida entre los 100 países se explica por la variación del "
  f"logaritmo del PIB per cápita. El {f(100*(1-G['r2']),1)} % restante se debe a otros factores que no están en el modelo, "
  "como el acceso a servicios de salud, la educación, la desigualdad, los conflictos armados, el VIH o la alimentación. "
  f"El R cuadrado corregido es {f(G['r2_aj'],4)}, prácticamente igual porque solo hay una variable explicativa. Se cumple "
  f"la identidad SCT = SCReg + SCRes: {f(G['sct'],2)} = {f(G['scr'],2)} + {f(G['sce'],2)}.")
P(f"En el Modelo 1 el coeficiente de determinación es apenas R² = {f(L['r2'],4)} ({f(100*L['r2'],1)} %). Es decir, solo "
  "con cambiar la forma funcional, sin agregar ninguna variable, la capacidad explicativa sube de 44 % a 79 %.")
tabla_resumen(lin, "Resumen del modelo(b) del Modelo 1, para comparar")
FIG("figuras/fig07_descomposicion.png", "Descomposición de la variación total de la esperanza de vida (Modelo 2)", 14)

H2("11. Análisis de varianza (ANOVA)")
P("La tabla ANOVA, en la estructura de salida de SPSS, prueba la significación global del modelo: H0: B = 0 (el modelo no explica nada) contra H1: B ≠ 0. "
  f"El valor crítico es F(0,05; 1; 98) = {f(G['Fcrit'],4)}.")
def tabla_anova(m, titulo):
    a = m.anova()
    filas = []
    for _, r in a.iterrows():
        filas.append([r["Fuente de variación"], f(r["Suma de cuadrados"], 4), str(int(r["Grados de libertad"])),
                      "" if np.isnan(r["Cuadrado medio"]) else f(r["Cuadrado medio"], 4),
                      "" if np.isnan(r["F calculado"]) else f(r["F calculado"], 2),
                      "" if np.isnan(r["Valor p"]) else fp(r["Valor p"])])
    TABLA(titulo, ["Fuente de variación", "Suma de cuadrados", "gl", "Cuadrado medio", "F", "Valor p"], filas, [3.8, 3.2, 1.3, 3.0, 2.0, 2.0])
tabla_anova_spss(log, "ANOVA(a) del Modelo 2: Y = a + b·ln(PIB)")
P(f"Como F = {f(G['F'],2)} > {f(G['Fcrit'],4)} (valor p < 0,001), rechazamos H0: el modelo es significativo en su "
  f"conjunto. Se cumple además que F = t² ({f(G['t_b'],4)}² = {f(G['t_b']**2,2)}), por lo que en regresión simple la "
  "prueba F y la prueba t de la pendiente llevan a la misma conclusión (equivalencia fundamental t_b² = F en la "
  "regresión simple). La media cuadrática residual, "
  f"CME = s_yx² = {f(G['s2'],4)} con 98 grados de libertad, es la estimación de σ², y su raíz es el error típico de la "
  f"estimación s_yx = {f(G['s'],3)} años. La tabla también verifica la identidad SCT = SCReg + SCRes.")
tabla_anova_spss(lin, "ANOVA(a) del Modelo 1: Y = a + b·PIB, para comparar")
P(f"El Modelo 1 también es significativo (F = {f(L['F'],2)}), pero su suma de cuadrados residual es {f(L['sce'],1)}, "
  f"más del doble que la del Modelo 2 ({f(G['sce'],1)}), lo que confirma que deja mucha más variación sin explicar.")

# ======================= CONCLUSIONES =======================
H1("Conclusiones y recomendaciones")
P("A partir del análisis de 100 países con datos de 2024 llegamos a las siguientes conclusiones:")
VIÑETA(f"Existe una relación positiva, fuerte y estadísticamente significativa entre el PIB per cápita y la esperanza de vida al "
       f"nacer. Todas las pruebas (t para B, t para ρ y F del ANOVA) rechazan la hipótesis nula con valores p menores que 0,001.")
VIÑETA("La relación no es lineal en el PIB en bruto. El diagrama de dispersión, el gráfico de residuos y la prueba RESET muestran "
       "que el ingreso tiene rendimientos decrecientes: los primeros miles de dólares se asocian con grandes ganancias en años de "
       "vida y, a partir de unos 20.000 a 30.000 dólares, la ganancia es pequeña.")
VIÑETA(f"El modelo con el logaritmo del PIB es el adecuado. Su ecuación es Ŷ = {f(G['a'],2)} + {f(G['b'],2)}·ln(PIB), con "
       f"r = {f(G['r'],3)} y R² = {f(G['r2'],3)}, frente a R² = {f(L['r2'],3)} del modelo lineal. Duplicar el PIB per cápita se "
       f"asocia con unos {f(G['b']*np.log(2),1)} años más de esperanza de vida.")
VIÑETA("Los supuestos se cumplen de forma razonable en el Modelo 2. Hay una leve falta de normalidad causada por pocos países "
       "atípicos y algo de heterocedasticidad, pero con 100 observaciones y con errores robustos las conclusiones no cambian.")
VIÑETA(f"Venezuela, con 4.244,5 dólares por persona, tiene una esperanza de vida de 72,67 años, un poco mayor que la que predice "
       f"el modelo ({f(iv['y0'],2)} años) y dentro de su intervalo de predicción. Las zonas azules, salvo Estados Unidos, viven "
       "más de lo que su ingreso predice, y las zonas rojas viven menos, lo que indica que factores como la salud pública, los "
       "hábitos de vida y los conflictos pesan además del dinero.")
P("Como recomendaciones para trabajos futuros proponemos: (1) usar el PIB per cápita en paridad de poder adquisitivo (PPA), "
  "que compara mejor el poder de compra entre países; (2) pasar a un modelo de regresión múltiple que incluya variables como "
  "el gasto en salud, los años de escolaridad o el acceso a agua potable, que podrían explicar parte del 21 % que el ingreso no "
  "explica; (3) estudiar la relación en varios años para ver si cambia con el tiempo, por ejemplo antes y después de la "
  "pandemia de COVID-19; y (4) tratar con cuidado los datos de Venezuela y de otros países con estadísticas oficiales "
  "limitadas, contrastándolos con otras fuentes como el Fondo Monetario Internacional o las Naciones Unidas.")
P("En lo práctico, el resultado sugiere que el crecimiento económico importa mucho más para la salud de los países pobres que "
  "para la de los ricos. Para un país como Venezuela, recuperar ingreso se asociaría con ganancias apreciables en esperanza de "
  "vida, pero los casos de Costa Rica o Sri Lanka muestran que con políticas de salud adecuadas se puede vivir más de lo que el "
  "ingreso haría esperar.")

# ======================= BIBLIOGRAFÍA =======================
H1("Bibliografía")
biblio = [
    "Asamblea General de las Naciones Unidas. (1948). Declaración Universal de los Derechos Humanos. París: ONU.",
    "Asamblea General de las Naciones Unidas. (2014). Principios Fundamentales de las Estadísticas Oficiales (A/RES/68/261). Nueva York: ONU.",
    "Asamblea General de las Naciones Unidas. (2015). Transformar nuestro mundo: la Agenda 2030 para el Desarrollo Sostenible (A/RES/70/1). Nueva York: ONU.",
    "Asamblea Nacional Constituyente. (1999). Constitución de la República Bolivariana de Venezuela. Caracas.",
    "Banco Mundial. (2025). Indicadores del Desarrollo Mundial: PIB per cápita (US$ a precios actuales) [NY.GDP.PCAP.CD] y esperanza de vida al nacer, total (años) [SP.DYN.LE00.IN]. Recuperado el 15 de noviembre de 2026 de https://datos.bancomundial.org",
    "Breusch, T. S. y Pagan, A. R. (1979). A simple test for heteroscedasticity and random coefficient variation. Econometrica, 47(5), 1287-1294.",
    "Buettner, D. (2008). The Blue Zones: Lessons for living longer from the people who've lived the longest. Washington: National Geographic.",
    "Gujarati, D. N. y Porter, D. C. (2010). Econometría (5.ª ed.). México: McGraw-Hill.",
    "Montgomery, D. C., Peck, E. A. y Vining, G. G. (2006). Introducción al análisis de regresión lineal (3.ª ed.). México: CECSA.",
    "Preston, S. H. (1975). The changing relation between mortality and level of economic development. Population Studies, 29(2), 231-248.",
    "Ramsey, J. B. (1969). Tests for specification errors in classical linear least-squares regression analysis. Journal of the Royal Statistical Society, Series B, 31(2), 350-371.",
    "República Bolivariana de Venezuela. (2001). Ley de la Función Pública de Estadística. Caracas: Gaceta Oficial.",
    "Seabold, S. y Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. Proceedings of the 9th Python in Science Conference, 92-96.",
    "Shapiro, S. S. y Wilk, M. B. (1965). An analysis of variance test for normality (complete samples). Biometrika, 52(3-4), 591-611.",
    "Walpole, R. E., Myers, R. H., Myers, S. L. y Ye, K. (2012). Probabilidad y estadística para ingeniería y ciencias (9.ª ed.). México: Pearson.",
    "White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. Econometrica, 48(4), 817-838.",
]
for b in biblio:
    p = doc.add_paragraph(b); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Cm(1.25); p.paragraph_format.first_line_indent = Cm(-1.25)
    p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(8)

# ======================= ANEXO =======================
salto()
H1("Anexo. Base de datos de los 100 países")
dd = df.sort_values("pais").reset_index(drop=True)
abrev = {"Ingreso alto": "Alto", "Ingreso mediano alto": "Med. alto", "Ingreso mediano bajo": "Med. bajo", "Ingreso bajo": "Bajo"}
grupo_txt = {"Zona azul": "Zona azul", "Zona roja": "Zona roja", "Venezuela": "Venezuela", "Otro": ""}
TABLA("Datos utilizados (año 2024)",
      ["N.º", "País", "ISO3", "Ingreso", "Grupo", "PIB pc (US$)", "Esp. de vida"],
      [[str(i + 1), r.pais, r.iso3, abrev[r.ingreso], grupo_txt[r.grupo], f(r.pib_pc_usd_2024, 1), f(r.esperanza_vida_2024, 2)] for i, r in dd.iterrows()],
      [1.1, 4.6, 1.4, 2.0, 2.2, 2.5, 2.0], tam=9, junta=False)

doc.save(SALIDA)
print("Guardado:", SALIDA)
