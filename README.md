# Regresión lineal bivariante: PIB per cápita y esperanza de vida (2024)

Trabajo de **Estadística II**, Escuela de Estadística y Ciencias Actuariales, Facultad de Ciencias Económicas y Sociales, Universidad Central de Venezuela.

- **Autores:** Allan Arcia y Eddie Palomino
- **Profesoras:** Sandra Pinto y Yuraisi Capriles

**App interactiva:** https://regresion-pib-esperanza-vida-uqp2vznznmjl5ge5z36kr8.streamlit.app

Estudiamos si el PIB per cápita explica la esperanza de vida al nacer en 100 países, incluyendo a Venezuela, los países de las zonas azules (Japón, Italia, Grecia, Costa Rica y Estados Unidos) y diez países de baja esperanza de vida que llamamos zonas rojas (Nigeria, Chad, República Centroafricana, Lesoto, Somalia, Malí, Guinea, Benín, Níger y Sierra Leona).

## Datos

Las dos variables salen de **una sola base oficial**: los Indicadores del Desarrollo Mundial (WDI) del Banco Mundial, año 2024. No se completó ningún dato con otras fuentes.

| Variable | Indicador WDI | Descripción |
|---|---|---|
| X | `NY.GDP.PCAP.CD` | PIB per cápita, US$ a precios actuales |
| Y | `SP.DYN.LE00.IN` | Esperanza de vida al nacer, total (años) |

- `data/pib_esperanza_vida_2024.csv`: la muestra de 100 países (iso3, país, región, nivel de ingreso, grupo, X, Y).
- `data/raw/wdi_2024_paises.csv`: copia de la descarga de la API del Banco Mundial para todos los países (15/11/2026).
- Se usó 2024 porque es el último año con ambos indicadores publicados. Sudán del Sur quedó fuera porque no tiene PIB de 2024.
- Licencia de los datos: CC BY 4.0 (Banco Mundial).

## Resultados principales

Todo el procesamiento se hizo en **IBM SPSS Statistics** con `spss/regresion_v6.sps`.

| | Y = a + b·X |
|---|---|
| Ecuación | Ŷ = 70,104 + 0,000177·X |
| r | 0,665 |
| r² | 0,442 |
| z de la pendiente | 8,81 (Sig. < 0,001) |
| F (ANOVA) | 77,632 (Sig. < 0,001) |
| Durbin-Watson | 1,929 |

La relación es positiva y significativa, pero moderada, y los gráficos de residuos muestran que no es lineal: el ingreso tiene rendimientos decrecientes. Para Venezuela (4.244,5 US$) la recta da 70,86 años; el valor observado es 72,67.

## Estructura

```
├── app.py                         # aplicación Streamlit (solo capturas de SPSS, más el mapa)
├── spss/regresion_v6.sps          # sintaxis de SPSS que produce todas las tablas y gráficos
├── figuras/spss_v6/               # capturas de la salida de SPSS
├── informe/generar_informe_v6.py  # arma el informe (normas APA) en Word y PDF a partir de las capturas
├── informe/contenido_v6.py        # texto del informe
├── descargar_datos.py             # arma la muestra (con --api vuelve a descargar del Banco Mundial)
└── data/                          # datos
```

## Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```
