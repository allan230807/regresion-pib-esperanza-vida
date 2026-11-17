"""Genera el informe v6 (normas APA, 7.ª ed.) en Word y PDF.

Todas las tablas y gráficos del informe son capturas de la salida de IBM SPSS
Statistics, guardadas en figuras/spss_v6/. El texto solo cita los valores que
aparecen en esas salidas o cálculos hechos a mano con ellos.

Uso (desde la raíz del repositorio):
    python informe/generar_informe_v6.py
Crea informe/Informe_Regresion_PIB_Esperanza_de_Vida_v6.docx y .pdf
(el PDF se hace con LibreOffice y el índice se pagina en dos pasadas).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
FIG = Path(os.environ.get("FIG_SPSS", RAIZ / "figuras" / "spss_v6"))
SALIDA = RAIZ / "informe" / "Informe_Regresion_PIB_Esperanza_de_Vida_v6.docx"
FUENTE = "Times New Roman"   # LibreOffice la dibuja con Liberation Serif (mismas métricas)
ANCHO_UTIL = 6.5             # pulgadas (carta con márgenes de 1 pulgada)
ESCALA_TABLAS = 0.85         # las tablas de SPSS se ponen al 85 % de su tamaño natural

sys.path.insert(0, str(RAIZ / "informe"))
from contenido_v6 import construir  # noqa: E402


# ---------------------------------------------------------------- estilos
def fijar_fuente(estilo, tam=12, negrita=None, cursiva=None):
    estilo.font.name = FUENTE
    estilo.font.size = Pt(tam)
    estilo.font.color.rgb = RGBColor(0, 0, 0)
    if negrita is not None:
        estilo.font.bold = negrita
    if cursiva is not None:
        estilo.font.italic = cursiva
    rpr = estilo.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), FUENTE)


def doble(pf, sangria=True):
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.first_line_indent = Inches(0.5) if sangria else Inches(0)


def campo_pagina(par):
    r = par.add_run()
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), tag)
        else:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = txt
        r._r.append(e)


MARCA = re.compile(r"(_\{[^}]*\}|\^\{[^}]*\}|\*[^*]+\*)")


class Informe:
    def __init__(self):
        self.doc = Document()
        d = self.doc
        sec = d.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, m, Inches(1))
        sec.header_distance = Inches(0.5)
        normal = d.styles["Normal"]
        fijar_fuente(normal)
        doble(normal.paragraph_format, sangria=False)
        for nombre, cursiva in (("Heading 1", False), ("Heading 2", False), ("Heading 3", True)):
            h = d.styles[nombre]
            fijar_fuente(h, 12, negrita=True, cursiva=cursiva)
            doble(h.paragraph_format, sangria=False)
            h.paragraph_format.keep_with_next = True
        d.styles["Heading 1"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hp = sec.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        campo_pagina(hp)
        self.n_tabla = 0
        self.n_figura = 0
        self.indice = []      # (nivel, texto)
        self.par_indice = {}  # texto -> párrafo del índice

    # -- texto con subíndices _{..}, superíndices ^{..} y cursivas *..*
    def corridas(self, p, texto, negrita=False, cursiva=False, tam=None):
        for trozo in MARCA.split(texto):
            if not trozo:
                continue
            r = None
            if trozo.startswith("_{"):
                r = p.add_run(trozo[2:-1]); r.font.subscript = True
            elif trozo.startswith("^{"):
                r = p.add_run(trozo[2:-1]); r.font.superscript = True
            elif trozo.startswith("*") and len(trozo) > 2:
                r = p.add_run(trozo[1:-1]); r.italic = True
            else:
                r = p.add_run(trozo)
            if negrita:
                r.bold = True
            if cursiva:
                r.italic = True
            if tam:
                r.font.size = Pt(tam)
        return p

    def p(self, texto, sangria=True, alin=None, **kw):
        par = self.doc.add_paragraph()
        doble(par.paragraph_format, sangria=sangria)
        if alin == "c":
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        return self.corridas(par, texto, **kw)

    def eq(self, texto):
        par = self.doc.add_paragraph()
        doble(par.paragraph_format, sangria=False)
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        return self.corridas(par, texto, cursiva=False)

    def salto(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        # el párrafo vacío que queda tras el salto no debe ocupar una línea doble
        par = self.doc.paragraphs[-1]
        par.paragraph_format.line_spacing = Pt(1)

    def h(self, nivel, texto, en_indice=True, nueva_pagina=False):
        par = self.doc.add_paragraph(style=f"Heading {nivel}")
        par.paragraph_format.page_break_before = nueva_pagina
        self.corridas(par, texto)
        if en_indice:
            self.indice.append((nivel, texto))
        return par

    def _imagen(self, nombres, ancho):
        """Una captura, o varias lado a lado (lista de nombres) repartiendo el ancho útil."""
        if isinstance(nombres, str):
            nombres = [nombres]
        par = self.doc.add_paragraph()
        doble(par.paragraph_format, sangria=False)
        par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        par.paragraph_format.keep_with_next = True
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if len(nombres) > 1:
            return self._imagenes_lado_a_lado(par, nombres)
        for k, nombre in enumerate(nombres):
            ruta = FIG / f"{nombre}.png"
            if k:
                par.add_run(" ")
            if ruta.exists():
                a = ancho
                if a is None:
                    # tamaño natural de la captura (exportada a 216 ppp), un poco reducido
                    a = Image.open(ruta).size[0] / 216 * ESCALA_TABLAS
                par.add_run().add_picture(str(ruta), width=Inches(min(a, ANCHO_UTIL)))
            else:
                par.add_run(f"[falta la captura de SPSS {nombre}.png]").bold = True
        return par

    def _imagenes_lado_a_lado(self, par, nombres):
        ancho = (ANCHO_UTIL - 0.2) / len(nombres)
        t = self.doc.add_table(rows=1, cols=len(nombres))
        t.autofit = False
        for k, nombre in enumerate(nombres):
            c = t.rows[0].cells[k]
            c.width = Inches(ancho + 0.1)
            cp = c.paragraphs[0]
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            ruta = FIG / f"{nombre}.png"
            if ruta.exists():
                cp.add_run().add_picture(str(ruta), width=Inches(ancho))
            else:
                cp.add_run(f"[falta la captura de SPSS {nombre}.png]").bold = True
        # la tabla va en lugar del párrafo vacío
        par._p.addnext(t._tbl)
        par._p.getparent().remove(par._p)
        return t

    def _rotulo(self, tipo, numero, titulo):
        a = self.doc.add_paragraph()
        doble(a.paragraph_format, sangria=False)
        a.paragraph_format.keep_with_next = True
        a.add_run(f"{tipo} {numero}").bold = True
        b = self.doc.add_paragraph()
        doble(b.paragraph_format, sangria=False)
        b.paragraph_format.keep_with_next = True
        self.corridas(b, titulo, cursiva=True)

    def _nota(self, nota):
        if not nota:
            return
        par = self.doc.add_paragraph()
        doble(par.paragraph_format, sangria=False)
        par.add_run("Nota. ").italic = True
        self.corridas(par, nota)

    def tabla(self, nombre, titulo, nota=None, ancho=None):
        self.n_tabla += 1
        self._rotulo("Tabla", self.n_tabla, titulo)
        self._imagen(nombre, ancho)
        self._nota(nota)
        return self.n_tabla

    def figura(self, nombre, titulo, nota=None, ancho=5.5):
        self.n_figura += 1
        self._rotulo("Figura", self.n_figura, titulo)
        self._imagen(nombre, ancho)
        self._nota(nota)
        return self.n_figura

    def referencia(self, texto):
        par = self.doc.add_paragraph()
        doble(par.paragraph_format, sangria=False)
        par.paragraph_format.left_indent = Inches(0.5)
        par.paragraph_format.first_line_indent = Inches(-0.5)
        self.corridas(par, texto)

    def tabla_datos(self, encabezados, filas, anchos):
        """Tabla de texto (solo para el apéndice con la base de datos)."""
        t = self.doc.add_table(rows=1, cols=len(encabezados))
        t.autofit = False
        for i, e in enumerate(encabezados):
            c = t.rows[0].cells[i]
            c.width = Inches(anchos[i])
            par = c.paragraphs[0]
            par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            r = par.add_run(e); r.bold = True; r.font.size = Pt(10)
        for fila in filas:
            celdas = t.add_row().cells
            for i, v in enumerate(fila):
                celdas[i].width = Inches(anchos[i])
                par = celdas[i].paragraphs[0]
                par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                if i >= len(fila) - 2:
                    par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                r = par.add_run(str(v)); r.font.size = Pt(10)
        # bordes al estilo APA: líneas arriba y abajo del encabezado y al final
        tblPr = t._tbl.tblPr
        bordes = OxmlElement("w:tblBorders")
        for lado in ("top", "bottom"):
            e = OxmlElement(f"w:{lado}")
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "8"); e.set(qn("w:color"), "000000")
            bordes.append(e)
        tblPr.append(bordes)
        for c in t.rows[0].cells:
            tcPr = c._tc.get_or_add_tcPr()
            b = OxmlElement("w:tcBorders")
            e = OxmlElement("w:bottom")
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "8"); e.set(qn("w:color"), "000000")
            b.append(e); tcPr.append(b)
        # repetir encabezado en cada página
        trPr = t.rows[0]._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
        return t

    # -- índice: se crea vacío y se rellena con las páginas reales
    def marcar_indice(self):
        self._pos_indice = len(self.doc.paragraphs)

    def escribir_indice(self, paginas):
        cuerpo = self.doc.element.body
        ancla = self.doc.paragraphs[self._pos_indice - 1]._p
        for nivel, texto in self.indice:
            par = self.doc.add_paragraph()
            pf = par.paragraph_format
            pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            pf.space_before = Pt(0); pf.space_after = Pt(0)
            pf.left_indent = Inches(0.35 * (nivel - 1))
            pf.tab_stops.add_tab_stop(Inches(ANCHO_UTIL), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            self.corridas(par, texto.replace("*", ""))
            par.add_run("\t" + str(paginas.get(texto, "")))
            cuerpo.remove(par._p)
            ancla.addnext(par._p)
            ancla = par._p

    def guardar(self, ruta):
        self.doc.save(ruta)


# ---------------------------------------------------------------- PDF e índice
def a_pdf(docx, carpeta):
    filtro = ('pdf:writer_pdf_Export:{"ReduceImageResolution":{"type":"boolean","value":"false"},'
              '"UseLosslessCompression":{"type":"boolean","value":"true"}}')
    subprocess.run(["soffice", "--headless", "--convert-to", filtro, "--outdir", str(carpeta), str(docx)],
                   capture_output=True, timeout=600, check=True)
    return Path(carpeta) / (Path(docx).stem + ".pdf")


def paginas_de(pdf, entradas, desde=3):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    n = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    textos = [subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", str(pdf), "-"],
                             capture_output=True, text=True).stdout for i in range(1, n + 1)]
    out = {}
    for nivel, e in entradas:
        limpio = e.replace("*", "").replace("_{", "").replace("^{", "").replace("}", "")
        for i in range(desde - 1, n):
            lineas = [l.strip() for l in textos[i].splitlines()]
            if any(l.startswith(limpio[:45]) for l in lineas):
                out[e] = i + 1
                break
    return out, n


def generar():
    previo = None
    with tempfile.TemporaryDirectory() as tmp:
        for _ in range(4):
            inf = Informe()
            construir(inf)
            inf.escribir_indice(previo or {})
            inf.guardar(SALIDA)
            pdf = a_pdf(SALIDA, tmp)
            pags, n = paginas_de(pdf, inf.indice)
            if pags == previo:
                break
            previo = pags
        faltan = [e for _, e in inf.indice if e not in pags]
        shutil.copy(pdf, SALIDA.with_suffix(".pdf"))
    print(f"{n} páginas. Índice: {pags}")
    if faltan:
        print("No se encontraron en el PDF:", faltan)


if __name__ == "__main__":
    generar()
