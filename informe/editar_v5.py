"""Aplica las correcciones de la versión 5 sobre la v4 (que contiene las salidas de SPSS).
Uso: python informe/editar_v5.py v4.docx v5.docx"""
import sys, re, copy
from docx import Document
from docx.shared import Pt

SUB = re.compile(r"_\{([^}]*)\}|_([A-Za-z0-9Ŷ|]+)")
d = Document(sys.argv[1])
P = d.paragraphs
txt = [p.text for p in P]

def buscar(inicio):
    idx = [i for i, t in enumerate(txt) if t.startswith(inicio)]
    assert len(idx) == 1, (inicio, idx)
    return P[idx[0]]

def limpiar(p):
    for el in list(p._p):
        if not el.tag.endswith("}pPr"):
            p._p.remove(el)

def escribir(p, partes, cursiva=False, tam=None):
    """partes: lista de (texto, estilo) con estilo '' o 'b'; _x o _{...} = subíndice."""
    limpiar(p)
    for texto, est in partes:
        pos = 0
        trozos = []
        for m in SUB.finditer(texto):
            trozos.append((texto[pos:m.start()], False)); trozos.append((m.group(1) or m.group(2), True)); pos = m.end()
        trozos.append((texto[pos:], False))
        for t, sub in trozos:
            if not t: continue
            r = p.add_run(t); r.bold = "b" in est; r.italic = cursiva
            if sub: r.font.subscript = True
            if tam: r.font.size = Pt(tam)

def nuevo_despues(ref, molde, partes, cursiva=False, tam=None):
    el = copy.deepcopy(molde._p); ref._p.addnext(el)
    from docx.text.paragraph import Paragraph
    np_ = Paragraph(el, ref._parent); escribir(np_, partes, cursiva, tam)
    return np_

cuerpo = buscar("La unidad de análisis es el país")
eq_molde = buscar("t = b / s")

# 1. Población y muestra
datos1 = buscar("Los datos se descargaron el 15 de noviembre")
nuevo_despues(datos1, cuerpo, [("Población y muestra. ", "b"), (
    "Siguiendo la distinción entre población y muestra del Tema 1 (muestreo), definimos la población objetivo como el "
    "conjunto de países y economías que reportan estadísticas oficiales ante el Banco Mundial. Es una población finita de "
    "N = 217 economías en 2024, según la clasificación de países del Banco Mundial. De ellas, 200 tienen publicados los dos "
    "indicadores para 2024 y forman el marco del que se tomó la muestra. La muestra está formada por n = 100 países, "
    "seleccionados para representar todas las regiones y los cuatro niveles de ingreso, e incluir los grupos de interés "
    "del estudio. En todo el informe, N mayúscula se refiere al tamaño de la población y n minúscula al tamaño de la "
    "muestra. Como la selección fue intencional y no aleatoria, las inferencias se interpretan bajo el supuesto de que la "
    "muestra es representativa de esa población.", "")])

# 2. Marco metódico: pruebas de los supuestos
escribir(buscar("Pruebas de los supuestos."), [("Pruebas de los supuestos. ", "b"), (
    "La normalidad de los residuos se verifica en primer lugar con la inspección del gráfico P-P normal de regresión de "
    "residuo tipificado y del histograma del residuo tipificado con curva normal; como pruebas de bondad de ajuste "
    "complementarias se usan Shapiro-Wilk, Kolmogorov-Smirnov con corrección de Lilliefors y Jarque-Bera. La "
    "homocedasticidad se verifica con la lectura visual del gráfico de dispersión del residuo tipificado (ZRESID) contra "
    "el pronóstico tipificado (ZPRED): los puntos deben formar una banda horizontal sin patrones, en particular sin "
    "forma de embudo. La linealidad se evalúa con el diagrama de dispersión bivariante y con la distribución aleatoria de "
    "los residuos en ese mismo gráfico. La independencia se revisa con el estadístico de Durbin-Watson, que debe estar "
    "cerca de 2. Este análisis gráfico de residuos es la herramienta de diagnóstico estándar de la cátedra de "
    "Estadística II. Las pruebas de Breusch-Pagan y de White (homocedasticidad) y la prueba RESET de Ramsey (linealidad) "
    "pertenecen a la Econometría y se presentan solo como ejercicio exploratorio complementario. En todas las pruebas "
    "analíticas la hipótesis nula es que el supuesto se cumple.", "")])

# 3. Punto 4
escribir(buscar("Verificamos los supuestos sobre los residuos"), [(
    "Verificamos los supuestos de los dos modelos siguiendo el criterio de la cátedra de Estadística II: el diagnóstico "
    "principal es el análisis gráfico de residuos que produce SPSS (diagrama de dispersión, gráfico P-P normal, "
    "histograma con curva normal y gráfico ZPRED vs ZRESID), junto con el estadístico de Durbin-Watson. La Tabla 5 "
    "resume, con α = 0,05, las pruebas analíticas que usamos como verificación complementaria; las de Breusch-Pagan, "
    "White y RESET se incluyen solo como ejercicio exploratorio, porque pertenecen a la Econometría.", "")])
t5 = buscar("Tabla 5.")
escribir(t5, [("Tabla 5. ", "b"), ("Pruebas analíticas complementarias de los supuestos sobre los residuos", "")], tam=11)
escribir(buscar("En el Modelo 1 el problema principal es la linealidad"), [(
    "En el Modelo 1 el problema principal es la linealidad. Ya el diagrama de dispersión del punto 3 mostraba una nube "
    "curva, y en el gráfico ZPRED vs ZRESID del Gráfico 5 los residuos forman un arco: negativos en los extremos y "
    "positivos en el centro. La prueba RESET lo confirma como verificación complementaria (p < 0,001). Además, en el "
    "gráfico P-P los puntos se alejan de la diagonal y las pruebas de normalidad rechazan H_0. Por eso no es "
    "recomendable usar el Modelo 1 para hacer inferencias ni predicciones.", "")])
escribir(buscar("En el Modelo 2 la situación mejora mucho"), [(
    "En el Modelo 2 la situación mejora mucho: el gráfico ZPRED vs ZRESID ya no muestra una curva y los puntos se "
    "reparten al azar alrededor de cero. Sobre cada supuesto concluimos lo siguiente:", "")])
escribir(buscar("Linealidad:"), [(
    "Linealidad: el criterio fundamental es gráfico. En el diagrama de dispersión bivariante inicial (punto 3, Gráfico 4) "
    "la nube de puntos frente a ln(PIB) forma una banda recta, y en el gráfico ZPRED vs ZRESID del Gráfico 6 los residuos "
    "se distribuyen de forma aleatoria alrededor de cero, sin la curva que sí aparece en el Modelo 1. Como verificación "
    "complementaria, la prueba RESET de Ramsey da p = 0,014, lo que sugiere una curvatura leve en los extremos que no "
    "altera las conclusiones.", "")])
escribir(buscar("Homocedasticidad:"), [(
    "Homocedasticidad: el diagnóstico estándar de la cátedra es la lectura visual del gráfico de residuos tipificados "
    "contra pronósticos tipificados (ZPRED vs ZRESID) generado por SPSS. En el Gráfico 6 los residuos forman una banda "
    "horizontal alrededor de cero, con casi todos los valores entre −2 y 2, y no aparece un patrón en forma de embudo que "
    "se abra o se cierre. Solo se nota una dispersión algo mayor en los pronósticos bajos y medios que en los altos, donde "
    "los países ricos se concentran entre 80 y 85 años. Concluimos que el supuesto se cumple de forma aceptable. Como "
    "ejercicio exploratorio complementario, propio de la Econometría y no exigido por el programa de Estadística II, "
    "aplicamos las pruebas de Breusch-Pagan (p = 0,005) y de White (p = 0,014), que detectan una heterocedasticidad "
    "leve, y recalculamos los errores estándar con el método robusto HC3: el error estándar de b pasa de 0,2332 a "
    "0,2500 y el estadístico t de 19,09 a 17,80, de modo que las conclusiones no cambian.", "")])

# 4. Punto 7: Z* y t de SPSS
p155 = buscar("Como |t| = 19,09 > 1,9845")
escribir(p155, [(
    "El procedimiento de regresión de SPSS (tabla Coeficientes(a)) reporta para la pendiente un estadístico t = 19,09 "
    "con Sig. < 0,001. De acuerdo con la guía docente de la cátedra para muestras grandes (n = 100 > 30), el estadístico "
    "de contraste formal se tipifica bajo la distribución normal estándar:", "")])
p_z = nuevo_despues(p155, eq_molde, [("Z* = (b − B_0) / s_b = (4,4519 − 0) / 0,2332 = 19,09", "")], cursiva=True)
nuevo_despues(p_z, cuerpo, [(
    "Las dos reglas de decisión son complementarias: como |Z*| = 19,09 > Z_{0,975} = 1,96 (o, de forma equivalente, "
    "|t*| = 19,09 > t_{(0,025; 98)} = 1,9845), se rechaza categóricamente H_0, con valor p (Sig.) < 0,001. Hay evidencia "
    "muy fuerte de que la pendiente poblacional es distinta de cero, es decir, el logaritmo del PIB per cápita sí explica "
    "la esperanza de vida. Además, como se verá en el punto 11, t_b² = 19,0883² = 364,36 = F de la tabla ANOVA, igualdad "
    "que siempre se cumple en la regresión simple.", "")])

# HC3 como complemento
escribir(buscar("Como vimos en los supuestos, hay algo de heterocedasticidad"), [(
    "Como ejercicio exploratorio complementario, propio de la Econometría y fuera del programa de Estadística II, la "
    "Tabla 9 compara los resultados con los errores estándar robustos HC3. Los intervalos casi no cambian y las "
    "conclusiones son las mismas.", "")])
t9 = buscar("Tabla 9.")
escribir(t9, [("Tabla 9. ", "b"), ("Inferencias sobre A y B (Modelo 2): errores estándar clásicos y robustos HC3 "
                                   "(ejercicio exploratorio complementario)", "")], tam=11)

# 5. Punto 9
p182 = buscar("Como 19,09 > 1,9845")
escribir(p182, [(
    "SPSS reporta para este contraste un estadístico t = 19,09 con Sig. < 0,001. Siguiendo la guía docente de la cátedra "
    "para muestras grandes (n = 100 > 30), el estadístico de contraste formal se tipifica bajo la normal estándar:", "")])
p_z2 = nuevo_despues(p182, eq_molde, [("Z* = r·√(n − 2) / √(1 − r²) = 19,09", "")], cursiva=True)
nuevo_despues(p_z2, cuerpo, [(
    "Como |Z*| = 19,09 > Z_{0,975} = 1,96 (o, de forma equivalente, |t*| = 19,09 > t_{(0,025; 98)} = 1,9845), se rechaza "
    "categóricamente H_0, con valor p (Sig.) < 0,001: existe una correlación lineal significativa entre las variables en "
    "la población. Este estadístico es exactamente igual al de la pendiente, como debe ocurrir en la regresión simple, y "
    "por lo tanto también se cumple t_b² = F del ANOVA.", "")])

# Conclusiones
escribir(buscar("Los supuestos se cumplen de forma razonable en el Modelo 2"), [(
    "Los supuestos se cumplen de forma razonable en el Modelo 2 según el análisis gráfico de residuos de SPSS: el "
    "gráfico P-P sigue la diagonal y el gráfico ZPRED vs ZRESID no muestra patrones. Las pruebas complementarias "
    "señalan una leve falta de normalidad, debida a pocos países atípicos, y algo de heterocedasticidad, pero con "
    "n = 100 las conclusiones no cambian.", "")])

# 6. Nota sobre N en las salidas de SPSS (después de los gráficos con histogramas de SPSS)
nota_molde = cuerpo
for ini in ["Gráfico 1.", "Gráfico 5.", "Gráfico 6."]:
    cap = buscar(ini)
    i = [k for k, p in enumerate(P) if p._p is cap._p][0]
    img = P[i + 1]; assert "graphicData" in img._p.xml
    nueva = nuevo_despues(img, nota_molde, [("Nota: N representa en la salida de SPSS el tamaño de la muestra analizada (n = 100).", "")],
                          cursiva=True, tam=9.5)
    nueva.paragraph_format.first_line_indent = None
    nueva.paragraph_format.line_spacing = 1.0
    nueva.paragraph_format.space_after = Pt(10)
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    nueva.alignment = WD_ALIGN_PARAGRAPH.LEFT

# 7. Bibliografía
sea = buscar("Seabold, S. y Perktold")
sea._p.getparent().remove(sea._p)

d.save(sys.argv[2])
print("ok")
