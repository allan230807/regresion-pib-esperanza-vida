* Encoding: UTF-8.
* =====================================================================.
* Estadística II - EECA - UCV. Regresión lineal bivariante (informe v6).
* X = PIB per cápita 2024 (US$ corrientes)   Y = esperanza de vida al nacer 2024 (años).
* Muestra: n = 100 países. Fuente: Banco Mundial, Indicadores del Desarrollo Mundial.
* Ejecutar desde la carpeta raíz del repositorio regresion-pib-esperanza-vida
* (si SPSS no encuentra el archivo, escribir la ruta completa en /FILE).
* Corrida con IBM SPSS Statistics 32 (Mac). En el Visor se cambiaron las etiquetas
* B -> b, t -> z, R -> r, R cuadrado -> r cuadrado y N -> n, y se dieron más decimales
* a la fila del PIB en la tabla Coeficientes.
* =====================================================================.

SET OLANG=SPANISH.
SET DECIMAL=DOT.
GET DATA /TYPE=TXT /FILE='data/pib_esperanza_vida_2024.csv' /ENCODING='UTF8'
  /DELIMITERS="," /QUALIFIER='"' /ARRANGEMENT=DELIMITED /FIRSTCASE=2
  /VARIABLES= iso3 A3 pais A40 region A60 ingreso A30 grupo A12 pib F12.1 esperanza F8.3.
EXECUTE.
SET DECIMAL=COMMA.

VARIABLE LABELS
  pib 'PIB per cápita 2024 (US$ corrientes)'
  esperanza 'Esperanza de vida al nacer 2024 (años)'
  pais 'País'
  region 'Región del Banco Mundial'.

RECODE ingreso ('Ingreso bajo'=1) ('Ingreso mediano bajo'=2) ('Ingreso mediano alto'=3) ('Ingreso alto'=4) INTO ning.
VARIABLE LABELS ning 'Nivel de ingreso (Banco Mundial)'.
VALUE LABELS ning 1 'Bajo' 2 'Mediano bajo' 3 'Mediano alto' 4 'Alto'.

RECODE grupo ('Zona azul'=1) ('Zona roja'=2) ('Venezuela'=3) ('Otro'=4) INTO gint.
VARIABLE LABELS gint 'Grupo de interés'.
VALUE LABELS gint 1 'Zonas azules' 2 'Zonas rojas' 3 'Venezuela' 4 'Resto de países'.
FORMATS ning gint (F1.0).
EXECUTE.

* ---- 1. Datos: composición de la muestra por región ---------------------.
MEANS TABLES=pib esperanza BY region
  /CELLS=COUNT MEAN.

* ---- 2. Estadísticos descriptivos e histogramas -------------------------.
FREQUENCIES VARIABLES=pib esperanza
  /FORMAT=NOTABLE
  /NTILES=4
  /STATISTICS=MEAN MEDIAN STDDEV RANGE MINIMUM MAXIMUM SKEWNESS SESKEW KURTOSIS SEKURT
  /HISTOGRAM
  /ORDER=ANALYSIS.

MEANS TABLES=pib esperanza BY ning
  /CELLS=COUNT MEAN MIN MAX.

MEANS TABLES=pib esperanza BY gint
  /CELLS=COUNT MEAN.

EXAMINE VARIABLES=esperanza BY ning
  /ID=pais
  /PLOT=BOXPLOT
  /STATISTICS=NONE
  /NOTOTAL.

* ---- 3. Diagrama de dispersión con la recta de mínimos cuadrados --------.
GGRAPH
  /GRAPHDATASET NAME="g" VARIABLES=pib esperanza MISSING=LISTWISE REPORTMISSING=NO
  /GRAPHSPEC SOURCE=INLINE.
BEGIN GPL
SOURCE: s=userSource(id("g"))
DATA: x=col(source(s), name("pib"))
DATA: y=col(source(s), name("esperanza"))
GUIDE: axis(dim(1), label("PIB per cápita 2024 (US$ corrientes)"))
GUIDE: axis(dim(2), label("Esperanza de vida al nacer 2024 (años)"))
GUIDE: text.title(label("Diagrama de dispersión"))
ELEMENT: point(position(x*y))
ELEMENT: line(position(smooth.linear(x*y)))
END GPL.

* ---- 9. Correlación de Pearson con su intervalo de confianza (z de Fisher) ----.
CORRELATIONS
  /VARIABLES=pib esperanza
  /PRINT=TWOTAIL NOSIG FULL
  /CI CILEVEL(95)
  /MISSING=PAIRWISE.

* ---- 4, 5, 7, 10 y 11. Regresión: Resumen del modelo, ANOVA, Coeficientes,.
* Durbin-Watson, histograma, gráfico P-P y dispersión ZPRED vs ZRESID.
* /SAVE guarda pronóstico e intervalos al 95 % (media: LMCI/UMCI; individual: LICI/UICI).
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS CI(95) R ANOVA
  /CRITERIA=PIN(.05) POUT(.10) CIN(95)
  /NOORIGIN
  /DEPENDENT esperanza
  /METHOD=ENTER pib
  /SCATTERPLOT=(*ZRESID ,*ZPRED)
  /RESIDUALS DURBIN HISTOGRAM(ZRESID) NORMPROB(ZRESID)
  /SAVE PRED SEPRED RESID ZRESID MCIN ICIN.

* Etiquetas en español para las variables que guarda REGRESSION.
VARIABLE LABELS ZRE_1 'Residuo estandarizado' PRE_1 'Pronóstico'
  LMCI_1 'Límite inferior media 95 %' UMCI_1 'Límite superior media 95 %'
  LICI_1 'Límite inferior individual 95 %' UICI_1 'Límite superior individual 95 %'.

* ---- 4. Pruebas de normalidad sobre el residuo estandarizado -------------.
EXAMINE VARIABLES=ZRE_1
  /PLOT NPPLOT
  /STATISTICS NONE
  /MISSING LISTWISE
  /NOTOTAL.

* ---- 8. Pronósticos e intervalos para Venezuela y países de contraste ----.
TEMPORARY.
SELECT IF ANY(iso3, 'VEN', 'NGA', 'CRI', 'JPN', 'USA').
SUMMARIZE
  /TABLES=pais pib esperanza PRE_1 LMCI_1 UMCI_1 LICI_1 UICI_1
  /FORMAT=LIST NOCASENUM NOTOTAL
  /TITLE='Pronósticos e intervalos al 95 %'
  /CELLS=NONE.
