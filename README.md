# Regresión lineal bivariante: PIB per cápita y esperanza de vida (2024)

Trabajo de **Estadística II**, Escuela de Estadística y Ciencias Actuariales, Facultad de Ciencias Económicas y Sociales, Universidad Central de Venezuela.

- **Autores:** Allan Arcia y Eddie Palomino
- **Profesoras:** Sandra Pinto y Yuraisi Carriles

**App interactiva:** https://regresion-pib-esperanza-vida-uqp2vznznmjl5ge5z36kr8.streamlit.app

Estudiamos si el PIB per cápita explica la esperanza de vida al nacer en 100 países, incluyendo a Venezuela, los países de las zonas azules (Japón, Italia, Grecia, Costa Rica y Estados Unidos) y diez países de baja esperanza de vida que llamamos zonas rojas (Nigeria, Chad, República Centroafricana, Lesoto, Somalia, Malí, Guinea, Benín, Níger y Sierra Leona).

## Datos

Las dos variables salen de **una sola base oficial**: los Indicadores del Desarrollo Mundial (WDI) del Banco Mundial, año 2024. No se completó ningún dato con otras fuentes.

| Variable | Indicador WDI | Descripción |
|---|---|---|
| X | `NY.GDP.PCAP.CD` | PIB per cápita, US$ a precios actuales |
| Y | `SP.DYN.LE00.IN` | Esperanza de vida al nacer, total (años) |

- `data/pib_esperanza_vida_2024.csv`: la muestra de 100 países (iso3, país, región, nivel de ingreso, grupo, X, Y).
- `data/raw/wdi_2024_paises.csv`: copia de la descarga de la API del Banco Mundial para todos los países (15/11/2026). El PIB está redondeado a 1 decimal y la esperanza de vida a 3 decimales.
- Se usó 2024 porque es el último año con ambos indicadores publicados. Sudán del Sur quedó fuera porque no tiene PIB de 2024.
- Licencia de los datos: CC BY 4.0 (Banco Mundial).

## Resultados principales

| | Modelo 1: Y = a + b·PIB | Modelo 2: Y = a + b·ln(PIB) |
|---|---|---|
| Ecuación | Ŷ = 70,1039 + 0,000177·PIB | **Ŷ = 33,9037 + 4,4519·ln(PIB)** |
| r | 0,6648 | **0,8877** |
| R² | 0,4420 | **0,7880** |
| F (ANOVA) | 77,63 | **364,36** |
| RESET (linealidad) | p < 0,001 | p = 0,014 |

La relación es curva, así que el modelo principal es el logarítmico. Duplicar el PIB per cápita se asocia con unos 3,09 años más de esperanza de vida. Para Venezuela (4.244,5 US$) el modelo predice 71,09 años, con intervalo de predicción al 95 % de (64,12; 78,06); el valor observado es 72,67.

## Estructura

```
├── app.py                      # aplicación Streamlit
├── src/regresion.py            # fórmulas del curso (MCO, t, F, intervalos, supuestos)
├── analisis.py                 # genera las figuras en figuras/
├── descargar_datos.py          # arma la muestra (con --api vuelve a descargar del Banco Mundial)
├── data/                       # datos
├── figuras/                    # gráficos del informe
├── informe/generar_informe.py  # genera el informe en Word
└── presentacion/               # respaldo en PDF de la exposición
```

El informe en Word y la app usan el mismo módulo `src/regresion.py`, por eso los números coinciden.

## Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

Para regenerar figuras e informe:

```bash
python analisis.py
pip install python-docx matplotlib
python informe/generar_informe.py informe/Informe.docx informe/paginas_indice.json
```
