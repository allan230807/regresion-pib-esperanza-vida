* Encoding: UTF-8.
* =====================================================================.
* Estadística II - EECA - UCV.
* Regresión lineal bivariante: PIB per cápita (X) y esperanza de vida (Y), 2024.
* Datos: Banco Mundial, Indicadores del Desarrollo Mundial (WDI).
* Uso: abrir en IBM SPSS Statistics (o PSPP) desde la carpeta raíz del
* repositorio y ejecutar todo (Ejecutar > Todo). Si SPSS no encuentra el
* archivo, escribir la ruta completa en /FILE.
* =====================================================================.

GET DATA
  /TYPE=TXT
  /FILE='data/pib_esperanza_vida_2024.csv'
  /ENCODING='UTF8'
  /DELIMITERS=","
  /QUALIFIER='"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /VARIABLES=
    iso3 A3
    pais A40
    region A60
    ingreso A30
    grupo A12
    pib F12.1
    esperanza F8.3.
EXECUTE.

VARIABLE LABELS
  pib 'PIB per cápita 2024 (US$ corrientes)'
  esperanza 'Esperanza de vida al nacer 2024 (años)'.

COMPUTE ln_pib = LN(pib).
VARIABLE LABELS ln_pib 'Logaritmo natural del PIB per cápita'.
EXECUTE.

* ---- 2. Estadísticas descriptivas -------------------------------------.
DESCRIPTIVES VARIABLES=pib ln_pib esperanza
  /STATISTICS=MEAN STDDEV VARIANCE MIN MAX SKEWNESS KURTOSIS.

EXAMINE VARIABLES=pib ln_pib esperanza
  /PLOT BOXPLOT HISTOGRAM
  /STATISTICS DESCRIPTIVES
  /PERCENTILES(25,50,75).

* ---- 9. Correlación de Pearson -----------------------------------------.
CORRELATIONS
  /VARIABLES=pib ln_pib esperanza
  /PRINT=TWOTAIL.

* ---- Modelo 1: Y = a + b*PIB --------------------------------------------.
REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA
  /DEPENDENT esperanza
  /METHOD=ENTER pib
  /RESIDUALS DURBIN.

* ---- Modelo 2 (principal): Y = a + b*ln(PIB) ----------------------------.
* Resumen del modelo, ANOVA, Coeficientes, Durbin-Watson, gráfico P-P,.
* histograma de residuos tipificados y dispersión ZPRED vs ZRESID.
* /SAVE guarda para cada país el pronóstico, los intervalos al 95 %.
* para la media (LMCI, UMCI) y para el valor individual (LICI, UICI).
REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA
  /CRITERIA=CIN(95)
  /DEPENDENT esperanza
  /METHOD=ENTER ln_pib
  /SCATTERPLOT=(*ZRESID ,*ZPRED)
  /RESIDUALS DURBIN HISTOGRAM(ZRESID) NORMPROB(ZRESID)
  /SAVE PRED SEPRED RESID ZRESID MCIN ICIN.

* ---- 4. Pruebas de normalidad sobre los residuos tipificados ------------.
EXAMINE VARIABLES=ZRE_1
  /PLOT NPPLOT
  /STATISTICS NONE.

* ---- 4. Breusch-Pagan (versión de Koenker): LM = n * R2 -----------------.
* Se regresa el residuo al cuadrado sobre ln_pib; LM sigue Chi2(1).
COMPUTE e2 = RES_1**2.
EXECUTE.
REGRESSION
  /STATISTICS R ANOVA
  /DEPENDENT e2
  /METHOD=ENTER ln_pib.

* ---- 8. Intervalos para Venezuela y países de contraste -----------------.
TEMPORARY.
SELECT IF (iso3='VEN' OR iso3='NGA' OR iso3='CRI' OR iso3='JPN' OR iso3='USA').
LIST VARIABLES=pais pib esperanza PRE_1 LMCI_1 UMCI_1 LICI_1 UICI_1.
