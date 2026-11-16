"""Recalcula los números de página del índice de un .docx (renderiza con LibreOffice).
Uso: python informe/actualizar_indice.py entrada.docx salida.docx"""
import sys, subprocess, re, os, shutil, tempfile
from docx import Document

ENTRADAS = ["Introducción", "I. Marco teórico", "1.1 Marco legal", "1.2 Marco metódico", "II. Desarrollo empírico",
            "1. Datos", "2. Estadísticas descriptivas y análisis", "3. Diagrama de dispersión y análisis",
            "4. Verificación de supuestos", "5. Estimación de los coeficientes y ecuación de regresión",
            "6. Interpretación de a y b", "7. Inferencias sobre A y B poblacionales",
            "8. Intervalo para la recta μy|x y para un valor particular Ya",
            "9. Inferencias sobre el coeficiente de correlación poblacional", "10. Coeficiente de determinación",
            "11. Análisis de varianza (ANOVA)", "Conclusiones y recomendaciones", "Bibliografía",
            "Anexo. Base de datos de los 100 países"]

def paginas(docx):
    tmp = tempfile.mkdtemp()
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, docx], capture_output=True, timeout=300)
    pdf = os.path.join(tmp, os.path.basename(docx)[:-5] + ".pdf")
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    pags = [subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", pdf, "-"], capture_output=True, text=True).stdout for i in range(1, n + 1)]
    out = {}
    for e in ENTRADAS:
        for i, t in enumerate(pags):
            if i < 2: continue
            if any(l.strip().startswith(e[:40]) and "....." not in l for l in t.splitlines()):
                out[e] = i + 1; break
    shutil.rmtree(tmp)
    return out, n

def fijar(docx_in, docx_out, pags):
    d = Document(docx_in)
    for p in d.paragraphs:
        if "\t" not in p.text: continue
        for e in ENTRADAS:
            if p.text.split("\t")[0] == e and e in pags:
                ult = p.runs[-1]
                ult.text = "\t" + str(pags[e])
    d.save(docx_out)

entrada, salida = sys.argv[1], sys.argv[2]
shutil.copy(entrada, salida)
prev = None
for _ in range(4):
    pags, n = paginas(salida)
    if pags == prev: break
    fijar(salida, salida, pags); prev = pags
assert len(pags) == len(ENTRADAS), pags
print(n, "páginas;", pags)
