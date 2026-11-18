"""Texto del informe v6. Lo usa generar_informe_v6.py.

Los números citados salen de la salida de SPSS (figuras/spss_v6/salida_v6.txt)
o de cálculos a mano con esos valores.
"""
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent


def es(x, d):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def clave_ref(texto):
    """Orden alfabético de las referencias sin tildes ni marcas de cursiva."""
    t = unicodedata.normalize("NFD", texto.replace("*", "")).encode("ascii", "ignore").decode()
    return t.lower()


def construir(inf):
    p, h, eq = inf.p, inf.h, inf.eq

    # ------------------------------------------------------------ portada
    inf.portada("REGRESIÓN LINEAL BIVARIANTE ENTRE EL PIB PER CÁPITA Y LA ESPERANZA DE VIDA AL NACER "
                "EN 100 PAÍSES EN EL AÑO 2024.",
                ["Sandra Pinto", "Yuraisi Capriles", "Joaquín Rangel"],
                ["Allan Arcia", "Eddie Palomino"],
                "Ciudad Universitaria, 17 de Noviembre de 2026")

    # ------------------------------------------------------------ índice
    h(1, "Índice", en_indice=False, nueva_pagina=True)
    inf.marcar_indice()

    # ------------------------------------------------------------ introducción
    h(1, "Introducción", nueva_pagina=True)
    p("Se suele decir que los países más ricos viven más. En este trabajo quisimos comprobarlo con las "
      "herramientas de Estadística II: tomamos 100 países y estudiamos si el producto interno bruto (PIB) "
      "per cápita sirve para explicar y predecir la esperanza de vida al nacer mediante un modelo de "
      "regresión lineal bivariante.")
    p("La variable independiente (X) es el PIB per cápita de 2024 en dólares corrientes y la variable "
      "dependiente (Y) es la esperanza de vida al nacer de 2024, en años. Las dos provienen de los "
      "Indicadores del Desarrollo Mundial del Banco Mundial (s. f.). La muestra incluye a Venezuela, a los "
      "cinco países donde están las llamadas zonas azules, regiones conocidas por la longevidad de su "
      "población (Buettner, 2012), y a diez países africanos con las esperanzas de vida más bajas, a los que "
      "llamamos zonas rojas.")
    p("El informe sigue el guion de la cátedra. Primero presentamos el marco legal y el marco metódico, y "
      "luego desarrollamos los once puntos del análisis: datos, estadísticas descriptivas, diagrama de "
      "dispersión, supuestos, estimación, interpretación, inferencias sobre los parámetros, intervalos, "
      "inferencia sobre la correlación, coeficiente de determinación y análisis de varianza. Todo el "
      "procesamiento se hizo en IBM SPSS Statistics 32 (IBM Corp., 2026) y todas las tablas y gráficos son "
      "capturas de su salida.")

    # ------------------------------------------------------------ marco teórico
    h(1, "I. Marco teórico")
    h(2, "1.1 Marco legal")
    p("Las dos variables del estudio tienen respaldo en normas nacionales e internacionales. La Constitución "
      "de la República Bolivariana de Venezuela (1999) establece en su artículo 83 que la salud es un "
      "derecho social fundamental y una obligación del Estado, que la garantiza como parte del derecho a la "
      "vida, y en su artículo 299 que el régimen socioeconómico debe asegurar el desarrollo humano integral. "
      "En el plano internacional, el artículo 25 de la Declaración Universal de Derechos Humanos (Asamblea "
      "General de las Naciones Unidas, 1948) reconoce el derecho a un nivel de vida adecuado que asegure la "
      "salud y el bienestar, y la Agenda 2030 (Asamblea General de las Naciones Unidas, 2015) incluye la "
      "salud y el bienestar (Objetivo 3) y el crecimiento económico (Objetivo 8), que son justamente "
      "nuestras dos variables.")
    p("En cuanto a los datos, el Decreto con Fuerza de Ley de la Función Pública de Estadística (2001) "
      "regula el Sistema "
      "Estadístico Nacional y la difusión de la estadística oficial en Venezuela, y los Principios "
      "Fundamentales de las Estadísticas Oficiales (Asamblea General de las Naciones Unidas, 2014) piden "
      "imparcialidad, transparencia en los métodos y acceso público. Los indicadores del Banco Mundial se "
      "publican con licencia Creative Commons Atribución 4.0, que permite usarlos citando la fuente.")

    h(2, "1.2 Marco metódico")
    p("El modelo de regresión lineal bivariante describe cómo cambia el valor medio de una variable "
      "dependiente Y cuando cambia una variable independiente X. En la población se plantea")
    eq("Y_{i} = A + B·X_{i} + e_{i},   i = 1, 2, …, n")
    p("donde A es el intercepto poblacional, B la pendiente poblacional y e_{i} el error aleatorio. La "
      "recta de regresión poblacional es μ_{y|x} = A + B·X. Como A y B son desconocidos, se estiman con "
      "una muestra de tamaño n y se obtiene la recta estimada Ŷ = a + b·X.", sangria=False)
    p("Los supuestos del modelo son: (1) la relación entre X y la media de Y es lineal; (2) los errores "
      "tienen media cero; (3) tienen varianza constante para todo valor de X (homocedasticidad); (4) son "
      "independientes entre sí; y (5) siguen una distribución normal.")
    p("Los estimadores de mínimos cuadrados minimizan la suma de los cuadrados de los residuos. Con "
      "S_{xx} = Σ(X − X̄)^{2}, S_{yy} = Σ(Y − Ȳ)^{2} y S_{xy} = Σ(X − X̄)(Y − Ȳ) se obtiene")
    eq("b = S_{xy} / S_{xx}        a = Ȳ − b·X̄")
    p("La varianza de los errores se estima con el cuadrado medio del error, s_{yx}^{2} = CME = SCRes / (n − 2), "
      "y su raíz s_{yx} es el error típico de la estimación.", sangria=False)
    p("Para las inferencias sobre A y B se usan los errores estándar s_{b} = s_{yx} / √S_{xx} y "
      "s_{a} = s_{yx}·√(1/n + X̄^{2}/S_{xx}). Como la muestra es grande (n > 30), el estadístico de "
      "contraste para H_{0}: B = 0 es z = b / s_{b}, y para H_{0}: A = 0 es z = a / s_{a}; se rechaza H_{0} "
      "si |z| > z_{1−α/2}, que con α = 0,05 es 1,96. Los intervalos de confianza son b ± z_{1−α/2}·s_{b} y "
      "a ± z_{1−α/2}·s_{a}.")
    p("Para un valor X_{0}, la estimación puntual es Ŷ_{0} = a + b·X_{0}. El intervalo para la media "
      "μ_{y|x0} y el intervalo para un valor particular Y_{a} usan los errores estándar")
    eq("S_{Ŷ0} = s_{yx}·√(1/n + (X_{0} − X̄)^{2}/S_{xx})        S_{Ya} = s_{yx}·√(1 + 1/n + (X_{0} − X̄)^{2}/S_{xx})")
    p("El intervalo para Y_{a} siempre es más ancho, porque además de la incertidumbre de la recta incluye "
      "la variación propia de cada observación.", sangria=False)
    p("El coeficiente de correlación de Pearson, r = S_{xy} / √(S_{xx}·S_{yy}), mide la intensidad de la "
      "relación lineal entre −1 y 1. Para H_{0}: ρ = 0 se usa z = r·√(n − 2) / √(1 − r^{2}), y el "
      "intervalo de confianza para ρ se construye con la transformación de Fisher, "
      "z_{r} = ½·ln[(1 + r)/(1 − r)], cuyo error estándar es 1/√(n − 3).")
    p("La variación total se descompone en SCT = SCReg + SCRes. El coeficiente de determinación "
      "r^{2} = SCReg / SCT es la proporción de la variación de Y explicada por X, y la tabla ANOVA prueba "
      "H_{0}: B = 0 con F = CMReg / CME, que tiene 1 y n − 2 grados de libertad.")
    p("Los supuestos se verifican con la salida de SPSS. La linealidad se juzga en el diagrama de "
      "dispersión y en el gráfico de residuos. La normalidad se revisa con el gráfico P-P normal y el "
      "histograma del residuo estandarizado: si los residuos son normales, los puntos del P-P siguen la "
      "diagonal y el histograma tiene forma de campana simétrica. La homocedasticidad se juzga en "
      "el gráfico de dispersión del residuo estandarizado (ZRESID) contra el pronóstico estandarizado "
      "(ZPRED): los puntos deben formar una banda horizontal sin forma de embudo. La independencia se "
      "revisa con el estadístico de Durbin-Watson, que debe estar cerca de 2.")

    # ------------------------------------------------------------ desarrollo empírico
    h(1, "II. Desarrollo empírico")

    # 1. Datos
    h(2, "1. Datos")
    p("Los datos se descargaron el 15 de noviembre de 2026 de los Indicadores del Desarrollo Mundial del "
      "Banco Mundial (s. f.): el indicador NY.GDP.PCAP.CD (PIB per cápita en dólares corrientes) y el "
      "SP.DYN.LE00.IN (esperanza de vida al nacer, ambos sexos). Las dos variables salen de esa única base "
      "para los 100 países, sin completar huecos con otras fuentes. Usamos 2024 porque es el año más "
      "reciente con ambos indicadores publicados.")
    p("La población está formada por las N = 217 economías que reportan al Banco Mundial; 200 de ellas "
      "tienen los dos indicadores de 2024. De ese marco tomamos una muestra de n = 100 países que cubre "
      "todas las regiones y niveles de ingreso e incluye a Venezuela, las cinco zonas azules (Japón, "
      "Italia, Grecia, Costa Rica y Estados Unidos) y las diez zonas rojas (Nigeria, Chad, República "
      "Centroafricana, Lesoto, Somalia, Malí, Guinea, Benín, Níger y Sierra Leona). La selección fue "
      "intencional, así que las inferencias suponen que la muestra representa a la población. Sudán del "
      "Sur quedó fuera porque no tiene PIB de 2024. La Tabla 1 resume la muestra por región y la base "
      "completa está en el apéndice.")
    inf.tabla("t01_region", "Composición de la muestra por región del Banco Mundial",
              "Salida de MEANS de IBM SPSS Statistics.")

    # 2. Descriptivas
    h(2, "2. Estadísticas descriptivas y análisis")
    inf.tabla("t02_estadisticos", "Estadísticos descriptivos del PIB per cápita y de la esperanza de vida",
              "Salida de FREQUENCIES de IBM SPSS Statistics.")
    p("El PIB per cápita es muy disperso y asimétrico. La media (20.178,84 dólares) casi triplica la "
      "mediana, la asimetría es de 2,06 y el coeficiente de variación, s/X̄ = 28.274,0/20.178,84, es de "
      "140,1 %. Es decir, hay muchos países de ingreso bajo y medio y unos pocos muy ricos que alargan la "
      "cola derecha (Figura 1). El valor mínimo es el de Afganistán (416,9 dólares) y el máximo el de "
      "Luxemburgo (137.781,7 dólares).")
    inf.figura("g01_hist_pib", "Histograma del PIB per cápita",
               "Salida de FREQUENCIES de IBM SPSS Statistics.", ancho=4.3)
    p("La esperanza de vida es mucho menos dispersa (coeficiente de variación de 10,2 %). Su media es "
      "73,68 años y su mediana 74,71 años, con una ligera asimetría negativa (−0,55): la cola izquierda "
      "la forman los países de las zonas rojas (Figura 2). El mínimo es Nigeria (54,63 años) y el máximo "
      "Suiza (84,41 años).")
    inf.figura("g02_hist_esperanza", "Histograma de la esperanza de vida al nacer",
               "Salida de FREQUENCIES de IBM SPSS Statistics.", ancho=4.3)
    p("Las Tablas 3 y 4 muestran el patrón que vamos a modelar. La esperanza de vida media sube de 62,5 "
      "años en los países de ingreso bajo a 81,0 años en los de ingreso alto, pero el aumento no es "
      "proporcional al dinero: pasar de ingreso bajo a mediano bajo (unos 1.600 dólares más) se asocia con "
      "5,5 años más de vida, mientras que pasar de mediano alto a alto (unos 41.700 dólares más) se asocia "
      "con 6,4 años. Entre los grupos de interés, las zonas azules promedian 40.775 dólares y 81,9 años, "
      "las zonas rojas apenas 1.004 dólares y 59,0 años, y Venezuela queda en un punto intermedio, con "
      "4.244,5 dólares y 72,7 años.")
    inf.tabla("t03_ingreso", "PIB per cápita y esperanza de vida según el nivel de ingreso",
              "Salida de MEANS de IBM SPSS Statistics.")
    inf.tabla("t04_grupos", "PIB per cápita y esperanza de vida según el grupo de interés",
              "Salida de MEANS de IBM SPSS Statistics.")

    # 3. Dispersión
    h(2, "3. Diagrama de dispersión y análisis")
    p("La Figura 3 muestra la nube de puntos con la recta de mínimos cuadrados. La relación es positiva, "
      "pero no sigue una recta: entre 0 y unos 20.000 dólares la esperanza de vida sube muy rápido, y a "
      "partir de allí la nube se aplana entre 80 y 85 años. La recta queda por encima de casi todos los "
      "países pobres de la izquierda, por debajo de muchos países de ingreso medio y otra vez por encima de "
      "los más ricos. Este rendimiento decreciente del ingreso ya había sido descrito por Preston (1975). "
      "También se ven casos llamativos: Nigeria y Chad viven unos 15 años menos de lo que da la recta, "
      "Estados Unidos vive menos que otros países ricos, y Guyana tiene casi 30.000 dólares por persona "
      "por el reciente auge petrolero, pero 70,3 años de esperanza de vida. Las líneas discontinuas son el "
      "intervalo de confianza al 95 % para la media de Y: es angosto cerca del PIB medio y se abre hacia "
      "los extremos, sobre todo en los PIB más altos, donde hay pocos países.")
    inf.figura("g04b_dispersion_ic", "Diagrama de dispersión de la esperanza de vida según el PIB per cápita",
               "Salida de GGRAPH de IBM SPSS Statistics, con la recta de mínimos cuadrados y los límites del "
               "intervalo de confianza al 95 % para la media.", ancho=5.5)

    # 4. Supuestos
    h(2, "4. Verificación de supuestos")
    p("Revisamos los supuestos con los gráficos de residuos que da el procedimiento REGRESIÓN de SPSS y "
      "con el estadístico de Durbin-Watson.")
    p("*Linealidad.* El diagrama de dispersión del punto 3 ya mostraba una nube curva, y el gráfico de "
      "residuos de la Figura 4 lo confirma: los residuos forman un arco, con muchos valores negativos en los "
      "pronósticos más bajos, positivos en el centro y otra vez negativos en los más altos. El supuesto de "
      "linealidad no se cumple.")
    inf.figura("g07_zpred_zresid", "Gráfico de dispersión del residuo estandarizado contra el pronóstico "
               "estandarizado", "Salida de REGRESIÓN de IBM SPSS Statistics.", ancho=4.6)
    p("*Homocedasticidad.* En la Figura 4 los residuos no forman una banda horizontal pareja. En los "
      "pronósticos más bajos, donde se agrupan los países pobres, los residuos van de casi −3 a poco más "
      "de 1, mientras que en los pronósticos altos hay pocos puntos y bajan siguiendo el arco. La varianza "
      "no parece constante, de modo que este supuesto tampoco se cumple con claridad.")
    p("*Normalidad.* En el gráfico P-P (Figura 5) los puntos se separan de la diagonal en la parte "
      "central, y el histograma (Figura 6) no es simétrico: tiene una cola larga a la izquierda, con "
      "residuos estandarizados cercanos a −3 (Nigeria y Chad). Los residuos no siguen una distribución "
      "normal.")
    inf.figura("g06_pp_zresid", "Gráfico P-P normal del residuo estandarizado",
               "Salida de REGRESIÓN de IBM SPSS Statistics.", ancho=3.6)
    inf.figura("g05_histograma_zresid", "Histograma del residuo estandarizado",
               "Salida de REGRESIÓN de IBM SPSS Statistics.", ancho=4.3)
    p("*Independencia.* Los datos son de corte transversal, un dato por país. El estadístico de "
      "Durbin-Watson, que aparece en la tabla Resumen del modelo del punto 10, es 1,929; como está muy "
      "cerca de 2, no hay indicios de autocorrelación de los residuos.")
    p("En resumen, el modelo cumple la independencia, pero no la linealidad ni la normalidad, y la "
      "homocedasticidad es dudosa. Por eso las inferencias y los intervalos de los puntos siguientes deben "
      "leerse con cautela.")

    # 5. Estimación
    h(2, "5. Estimación de los coeficientes y ecuación de regresión")
    p("Con n = 100, X̄ = 20.178,843, Ȳ = 73,6848, S_{xx} = 79.142.486.769,1 y S_{xy} = 14.044.679,0 "
      "obtenemos")
    eq("b = 14.044.679,0 / 79.142.486.769,1 = 0,000177")
    eq("a = 73,6848 − 0,000177 × 20.178,843 = 70,104")
    p("La Tabla 5 es la salida de SPSS: en la fila (Constante) está a y en la fila del PIB está b. La "
      "ecuación estimada es", sangria=False)
    eq("Ŷ = 70,104 + 0,000177·X")
    inf.tabla("t08_coeficientes", "Coeficientes del modelo",
              "Salida de REGRESIÓN de IBM SPSS Statistics. Variable dependiente: esperanza de vida al nacer "
              "2024 (años).")

    # 6. Interpretación
    h(2, "6. Interpretación de a y b")
    p("La pendiente b = 0,000177 indica que por cada dólar adicional de PIB per cápita la esperanza de "
      "vida aumenta en promedio 0,000177 años, es decir, unos 1,77 años por cada 10.000 dólares. El "
      "intercepto a = 70,10 sería la esperanza de vida de un país con PIB per cápita igual a cero. Ese "
      "valor está fuera del rango observado (de 417 a 137.782 dólares), así que no tiene una "
      "interpretación práctica. Además, muestra el problema del modelo: los países más pobres viven en "
      "promedio unos 59 años (zonas rojas), muy por debajo de los 70 años que da la recta en ese extremo.")

    # 7. Inferencias sobre A y B
    h(2, "7. Inferencias sobre A y B poblacionales")
    p("Trabajamos con α = 0,05, de modo que el valor crítico es z_{0,975} = 1,96. Los valores de b, "
      "s_{b}, z y Sig. están en la Tabla 5.")
    p("*Pendiente B.* H_{0}: B = 0 (el PIB per cápita no explica la esperanza de vida) contra "
      "H_{1}: B ≠ 0.")
    eq("z = b / s_{b} = 0,000177 / 0,0000201 = 8,81")
    p("Como |z| = 8,81 > 1,96 (Sig. < 0,001), rechazamos H_{0}: la pendiente poblacional es distinta de "
      "cero y el PIB per cápita sí está relacionado con la esperanza de vida.", sangria=False)
    p("*Intercepto A.* H_{0}: A = 0 contra H_{1}: A ≠ 0.")
    eq("z = a / s_{a} = 70,104 / 0,697 = 100,54")
    p("Como |z| = 100,54 > 1,96 (Sig. < 0,001), también rechazamos H_{0}.", sangria=False)
    p("*Intervalos de confianza al 95 %.*")
    eq("B: 0,000177 ± 1,96 × 0,0000201 → (0,000138 ; 0,000217)")
    eq("A: 70,104 ± 1,96 × 0,697 → (68,737 ; 71,471)")
    p("Con 95 % de confianza, cada 10.000 dólares adicionales de PIB per cápita se asocian en la población "
      "con un aumento de entre 1,38 y 2,17 años de esperanza de vida. Ningún intervalo contiene el cero, "
      "lo que coincide con las pruebas. Los límites que da SPSS en la Tabla 5, (0,000137; 0,000217) para B "
      "y (68,720; 71,488) para A, difieren de los nuestros solo en la tercera cifra decimal, porque SPSS "
      "los calcula con 98 grados de libertad.", sangria=False)

    # 8. Intervalos
    h(2, "8. Intervalo para la recta μ_{y|x} y para un valor particular Y_{a}")
    p("Aplicamos los intervalos a Venezuela, con X_{0} = 4.244,5 dólares. La estimación puntual es")
    eq("Ŷ_{0} = 70,104 + 0,000177 × 4.244,5 = 70,86 años")
    p("Con s_{yx} = 5,666, n = 100, X̄ = 20.178,843 y S_{xx} = 79.142.486.769,1, los errores estándar son",
      sangria=False)
    eq("S_{Ŷ0} = 5,666·√(1/100 + (4.244,5 − 20.178,843)^{2} / 79.142.486.769,1) = 0,651")
    eq("S_{Ya} = 5,666·√(1 + 1/100 + (4.244,5 − 20.178,843)^{2} / 79.142.486.769,1) = 5,703")
    p("y los intervalos al 95 % son", sangria=False)
    eq("μ_{y|x0}: 70,86 ± 1,96 × 0,651 → (69,58 ; 72,13) años")
    eq("Y_{a}: 70,86 ± 1,96 × 5,703 → (59,68 ; 82,04) años")
    p("Con 95 % de confianza, la esperanza de vida media de los países con un PIB per cápita de 4.244,5 "
      "dólares está entre 69,58 y 72,13 años, y para un país en particular con ese ingreso, como "
      "Venezuela, esperamos que esté entre 59,68 y 82,04 años. El valor observado de Venezuela, 72,67 "
      "años, cae dentro del intervalo y está 1,81 años por encima del pronóstico. La Tabla 6 muestra los "
      "intervalos que calcula SPSS para Venezuela y cuatro países de contraste (con 98 grados de libertad, "
      "por eso varían en la primera o segunda cifra decimal).", sangria=False)
    inf.tabla("t10_intervalos", "Pronósticos e intervalos al 95 % para Venezuela y países de contraste",
              "Salida de RESÚMENES DE CASOS de IBM SPSS Statistics a partir de los valores que guarda "
              "REGRESIÓN.")
    p("El intervalo de predicción es de unos ±11 años, demasiado ancho para ser útil, y crece lejos de X̄: "
      "para Estados Unidos el límite superior pasa de 97 años, un valor que ningún país alcanza. Nigeria, "
      "con 54,63 años, queda por debajo de su intervalo. Ambos casos reflejan que la recta no describe "
      "bien los extremos de la nube.")

    # 9. Correlación
    h(2, "9. Inferencias sobre el coeficiente de correlación poblacional")
    p("El coeficiente de correlación muestral es r = 0,665 (Tabla 7), una correlación positiva y moderada. "
      "Planteamos H_{0}: ρ = 0 contra H_{1}: ρ ≠ 0, con α = 0,05.")
    eq("z = r·√(n − 2) / √(1 − r^{2}) = 0,6648 × √98 / √(1 − 0,4420) = 8,81")
    p("Como |z| = 8,81 > 1,96 (Sig. < 0,001), rechazamos H_{0}: hay correlación lineal entre las dos "
      "variables en la población. El valor coincide con el de la pendiente, como debe ocurrir en la "
      "regresión bivariante. Esto no contradice el punto 4: hay una tendencia lineal significativa, pero "
      "la relación verdadera es curva, y por eso r es solo moderado.", sangria=False)
    inf.tabla("t05_correlaciones", "Correlación de Pearson entre el PIB per cápita y la esperanza de vida",
              "Salida de CORRELACIONES de IBM SPSS Statistics.")
    p("Para el intervalo usamos la transformación de Fisher: z_{r} = ½·ln(1,6648/0,3352) = 0,8014, con "
      "error estándar 1/√97 = 0,1015. El intervalo para z_{r} es 0,8014 ± 1,96 × 0,1015 = (0,6024; "
      "1,0004) y, al devolverlo a la escala de r, queda")
    eq("IC 95 % para ρ: (0,539 ; 0,762)")
    p("Con 95 % de confianza, la correlación poblacional está entre 0,54 y 0,76. SPSS da exactamente el "
      "mismo intervalo (Tabla 8).", sangria=False)
    inf.tabla("t05b_ic_correlacion", "Intervalo de confianza al 95 % para la correlación poblacional",
              "Salida de CORRELACIONES de IBM SPSS Statistics, con la transformación z de Fisher.")

    # 10. Determinación
    h(2, "10. Coeficiente de determinación")
    inf.tabla("t06_resumen", "Resumen del modelo",
              "Salida de REGRESIÓN de IBM SPSS Statistics. Predictor: (Constante), PIB per cápita 2024. "
              "Variable dependiente: esperanza de vida al nacer 2024.")
    eq("r^{2} = SCReg / SCT = 2.492,378 / 5.638,653 = 0,442")
    p("El 44,2 % de la variación de la esperanza de vida entre los 100 países se explica por el PIB per "
      "cápita. El 55,8 % restante depende de otros factores que no están en el modelo, como el acceso a "
      "la salud, la educación, los conflictos armados o las enfermedades, y también de la forma curva de "
      "la relación, que la recta no recoge. El r cuadrado ajustado es 0,436 y el error típico de la "
      "estimación es 5,666 años.")

    # 11. ANOVA
    h(2, "11. Análisis de varianza (ANOVA)")
    p("La tabla ANOVA prueba la significación global del modelo: H_{0}: B = 0 contra H_{1}: B ≠ 0. El "
      "valor crítico es F_{(0,05; 1; 98)} = 3,94.")
    inf.tabla("t07_anova", "Análisis de varianza del modelo",
              "Salida de REGRESIÓN de IBM SPSS Statistics. Variable dependiente: esperanza de vida al nacer "
              "2024. Predictor: (Constante), PIB per cápita 2024.")
    p("Como F = 77,632 > 3,94 (Sig. < 0,001), rechazamos H_{0}: el modelo es significativo. Se cumple que "
      "SCT = SCReg + SCRes (5.638,653 = 2.492,378 + 3.146,274) y que F = z^{2} de la pendiente "
      "(8,811^{2} = 77,63). La media cuadrática residual, CME = 32,105, es la estimación de la varianza de "
      "los errores, y su raíz es el error típico de la estimación, s_{yx} = 5,666 años.")

    # ------------------------------------------------------------ conclusiones
    h(1, "Conclusiones y recomendaciones")
    p("Hay una relación positiva y estadísticamente significativa entre el PIB per cápita y la esperanza "
      "de vida al nacer. La prueba sobre B, la prueba sobre ρ y la F del ANOVA rechazan la hipótesis nula "
      "con Sig. < 0,001. La recta estimada es Ŷ = 70,104 + 0,000177·X: cada 10.000 dólares de PIB per "
      "cápita se asocian con unos 1,77 años más de vida.")
    p("La relación es moderada: r = 0,665 y el modelo explica el 44,2 % de la variación. El diagrama de "
      "dispersión y los residuos muestran que el ingreso tiene rendimientos decrecientes, porque los "
      "primeros miles de dólares se asocian con grandes ganancias de vida y luego la nube se aplana. Por "
      "eso no se cumplen los supuestos de linealidad ni de normalidad, la homocedasticidad es dudosa, y "
      "las predicciones fallan en los extremos (por ejemplo, la recta da más de 89 años a Suiza, que vive "
      "84,4). Solo la independencia se cumple (Durbin-Watson = 1,929).")
    p("Venezuela, con 4.244,5 dólares por persona, vive 72,67 años, un poco más de lo que da el modelo "
      "(70,86) y dentro de su intervalo de predicción. Las zonas azules, salvo Estados Unidos, viven más de "
      "lo que predice su ingreso, y las zonas rojas mucho menos, lo que indica que la salud pública, los "
      "hábitos y los conflictos pesan además del dinero.")
    p("Para trabajos futuros recomendamos agregar otras variables explicativas, como el gasto en salud o "
      "los años de escolaridad, comparar varios años para ver si la relación cambia, y tratar con cuidado "
      "los datos de Venezuela, cuyas cuentas nacionales tienen más incertidumbre por la poca publicación "
      "de cifras oficiales.")

    # ------------------------------------------------------------ referencias
    h(1, "Referencias", nueva_pagina=True)
    for r in sorted(REFERENCIAS, key=clave_ref):
        inf.referencia(r)

    # ------------------------------------------------------------ apéndice
    h(1, "Apéndice. Base de datos de los 100 países", nueva_pagina=True)
    df = pd.read_csv(RAIZ / "data" / "pib_esperanza_vida_2024.csv").sort_values("pais")
    ing = {"Ingreso bajo": "Bajo", "Ingreso mediano bajo": "Mediano bajo",
           "Ingreso mediano alto": "Mediano alto", "Ingreso alto": "Alto"}
    gru = {"Otro": "", "Zona azul": "Zona azul", "Zona roja": "Zona roja", "Venezuela": "Venezuela"}
    filas = [(i + 1, r.pais, r.iso3, ing[r.ingreso], gru[r.grupo], es(r.pib_pc_usd_2024, 1),
              es(r.esperanza_vida_2024, 2)) for i, r in enumerate(df.itertuples())]
    p("Datos de 2024 del Banco Mundial (s. f.). PIB per cápita en dólares corrientes y esperanza de vida "
      "al nacer en años.", sangria=False)
    inf.tabla_datos(["N.º", "País", "ISO3", "Ingreso", "Grupo", "PIB per cápita (US$)", "Esperanza de vida"],
                    filas, [0.45, 1.7, 0.55, 1.05, 0.95, 1.0, 0.8])


REFERENCIAS = [
    "Asamblea General de las Naciones Unidas. (1948). *Declaración Universal de Derechos Humanos* "
    "(Resolución 217 A [III]). https://www.un.org/es/about-us/universal-declaration-of-human-rights",
    "Asamblea General de las Naciones Unidas. (2014). *Principios Fundamentales de las Estadísticas "
    "Oficiales* (A/RES/68/261). https://undocs.org/es/A/RES/68/261",
    "Asamblea General de las Naciones Unidas. (2015). *Transformar nuestro mundo: la Agenda 2030 para el "
    "Desarrollo Sostenible* (A/RES/70/1). https://undocs.org/es/A/RES/70/1",
    "Banco Mundial. (s. f.). *Indicadores del Desarrollo Mundial* [Conjunto de datos]. Recuperado el 15 de "
    "noviembre de 2026 de https://databank.bancomundial.org/source/world-development-indicators",
    "Buettner, D. (2012). *The blue zones: 9 lessons for living longer from the people who've lived the "
    "longest* (2.ª ed.). National Geographic.",
    "Constitución de la República Bolivariana de Venezuela. (1999, 30 de diciembre). *Gaceta Oficial de "
    "la República Bolivariana de Venezuela*, 36.860.",
    "IBM Corp. (2026). *IBM SPSS Statistics para Mac* (Versión 32.0) [Software]. IBM Corp.",
    "Decreto con Fuerza de Ley de la Función Pública de Estadística. (2001, 9 de noviembre). *Gaceta "
    "Oficial de la República Bolivariana de Venezuela*, 37.321.",
    "Preston, S. H. (1975). The changing relation between mortality and level of economic development. "
    "*Population Studies, 29*(2), 231-248. https://doi.org/10.1080/00324728.1975.10410201",
]
