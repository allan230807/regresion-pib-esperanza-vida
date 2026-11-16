* Encoding: UTF-8.
* Salida de SPSS en español (gráficos y tablas usados en el informe v4).
* Ejecutar desde la carpeta raíz del repositorio; si no encuentra el archivo, poner la ruta completa en /FILE.
SET LOCALE='es_ES'. 
SET OLANG=SPANISH DECIMAL=DOT.
GET DATA /TYPE=TXT /FILE='data/pib_esperanza_vida_2024.csv' /ENCODING='UTF8'
  /DELIMITERS="," /QUALIFIER='"' /ARRANGEMENT=DELIMITED /FIRSTCASE=2
  /VARIABLES= iso3 A3 pais A40 region A60 ingreso A30 grupo A12 pib F12.1 esperanza F8.3.
EXECUTE.
SET DECIMAL=COMMA.
VARIABLE LABELS pib 'PIB per cápita 2024 (US$ corrientes)' esperanza 'Esperanza de vida al nacer 2024 (años)'.
COMPUTE ln_pib = LN(pib).
VARIABLE LABELS ln_pib 'Logaritmo natural del PIB per cápita'.
RECODE ingreso ('Ingreso bajo'=1) ('Ingreso mediano bajo'=2) ('Ingreso mediano alto'=3) ('Ingreso alto'=4) INTO ning.
VARIABLE LABELS ning 'Nivel de ingreso (Banco Mundial)'.
VALUE LABELS ning 1 'Bajo' 2 'Mediano bajo' 3 'Mediano alto' 4 'Alto'.
EXECUTE.
EXAMINE VARIABLES=pib ln_pib esperanza /PLOT HISTOGRAM /STATISTICS NONE.
EXAMINE VARIABLES=pib esperanza BY ning /ID=pais /PLOT BOXPLOT /STATISTICS NONE /NOTOTAL.
GGRAPH /GRAPHDATASET NAME="g" VARIABLES=pib esperanza /GRAPHSPEC SOURCE=INLINE.
BEGIN GPL
SOURCE: s=userSource(id("g"))
DATA: x=col(source(s), name("pib"))
DATA: y=col(source(s), name("esperanza"))
GUIDE: axis(dim(1), label("PIB per cápita 2024 (US$ corrientes)"))
GUIDE: axis(dim(2), label("Esperanza de vida al nacer 2024 (años)"))
GUIDE: text.title(label("Dispersión de la esperanza de vida según el PIB per cápita"))
ELEMENT: point(position(x*y))
ELEMENT: line(position(smooth.linear(x*y)))
END GPL.
GGRAPH /GRAPHDATASET NAME="g" VARIABLES=ln_pib esperanza /GRAPHSPEC SOURCE=INLINE.
BEGIN GPL
SOURCE: s=userSource(id("g"))
DATA: x=col(source(s), name("ln_pib"))
DATA: y=col(source(s), name("esperanza"))
GUIDE: axis(dim(1), label("Logaritmo natural del PIB per cápita"))
GUIDE: axis(dim(2), label("Esperanza de vida al nacer 2024 (años)"))
GUIDE: text.title(label("Dispersión de la esperanza de vida según ln(PIB per cápita)"))
ELEMENT: point(position(x*y))
ELEMENT: line(position(smooth.linear(x*y)))
END GPL.
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT esperanza /METHOD=ENTER pib
  /SCATTERPLOT=(*ZRESID ,*ZPRED) /RESIDUALS DURBIN HISTOGRAM(ZRESID) NORMPROB(ZRESID) /SAVE ZRESID(ZR_M1).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /CRITERIA=CIN(95) /DEPENDENT esperanza /METHOD=ENTER ln_pib
  /SCATTERPLOT=(*ZRESID ,*ZPRED) /RESIDUALS DURBIN HISTOGRAM(ZRESID) NORMPROB(ZRESID)
  /SAVE PRED SEPRED RESID ZRESID MCIN ICIN.
EXAMINE VARIABLES=ZR_M1 ZRE_1 /PLOT NPPLOT /STATISTICS NONE.
