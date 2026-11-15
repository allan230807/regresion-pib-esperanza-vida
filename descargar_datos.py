"""Arma la muestra de 100 países con datos del Banco Mundial (WDI), año 2024.

Ambas variables salen de una sola base oficial, los Indicadores del Desarrollo Mundial:
  X = NY.GDP.PCAP.CD  PIB per cápita (US$ a precios actuales)
  Y = SP.DYN.LE00.IN  Esperanza de vida al nacer, total (años)

Uso:  python descargar_datos.py          (usa la copia guardada en data/raw/)
      python descargar_datos.py --api    (vuelve a descargar desde la API del Banco Mundial)
"""
import sys
import pandas as pd

ANIO = 2024
RAW = "data/raw/wdi_2024_paises.csv"
INDICADORES = {"NY.GDP.PCAP.CD": "pib_pc_usd_2024", "SP.DYN.LE00.IN": "esperanza_vida_2024"}


def desde_api():
    import requests
    datos = {}
    for cod in INDICADORES:
        url = f"https://api.worldbank.org/v2/country/all/indicator/{cod}?date={ANIO}&format=json&per_page=400"
        filas = requests.get(url, timeout=60).json()[1]
        datos[f"{cod}_{ANIO}"] = {r["countryiso3code"]: r["value"] for r in filas if r["value"] is not None and r["countryiso3code"]}
    df = pd.DataFrame(datos).rename_axis("iso3").reset_index()
    df.to_csv(RAW, index=False)
    return df


wdi = desde_api() if "--api" in sys.argv else pd.read_csv(RAW)
wdi = wdi.set_index("iso3")
gdp, le = wdi[f"NY.GDP.PCAP.CD_{ANIO}"].to_dict(), wdi[f"SP.DYN.LE00.IN_{ANIO}"].to_dict()

LAC, NAM, ECA, EAP, MNA, SAS, SSA = ("América Latina y el Caribe","América del Norte","Europa y Asia Central",
 "Asia Oriental y el Pacífico","Oriente Medio, Norte de África, Afganistán y Pakistán","Asia Meridional","África Subsahariana")
# iso: (nombre, región BM, ingreso BM, grupo)
P = {
"VEN":("Venezuela",LAC,"Ingreso mediano bajo","Venezuela"),
"JPN":("Japón",EAP,"Ingreso alto","Zona azul"),"ITA":("Italia",ECA,"Ingreso alto","Zona azul"),
"GRC":("Grecia",ECA,"Ingreso alto","Zona azul"),"CRI":("Costa Rica",LAC,"Ingreso alto","Zona azul"),
"USA":("Estados Unidos",NAM,"Ingreso alto","Zona azul"),
"NGA":("Nigeria",SSA,"Ingreso mediano bajo","Zona roja"),"TCD":("Chad",SSA,"Ingreso bajo","Zona roja"),
"CAF":("República Centroafricana",SSA,"Ingreso bajo","Zona roja"),"LSO":("Lesoto",SSA,"Ingreso mediano bajo","Zona roja"),
"SOM":("Somalia",SSA,"Ingreso bajo","Zona roja"),"MLI":("Malí",SSA,"Ingreso bajo","Zona roja"),
"GIN":("Guinea",SSA,"Ingreso mediano bajo","Zona roja"),"BEN":("Benín",SSA,"Ingreso mediano bajo","Zona roja"),
"NER":("Níger",SSA,"Ingreso bajo","Zona roja"),"SLE":("Sierra Leona",SSA,"Ingreso bajo","Zona roja"),
"ARG":("Argentina",LAC,"Ingreso mediano alto","Otro"),"BOL":("Bolivia",LAC,"Ingreso mediano bajo","Otro"),
"BRA":("Brasil",LAC,"Ingreso mediano alto","Otro"),"CHL":("Chile",LAC,"Ingreso alto","Otro"),
"COL":("Colombia",LAC,"Ingreso mediano alto","Otro"),"DOM":("República Dominicana",LAC,"Ingreso mediano alto","Otro"),
"ECU":("Ecuador",LAC,"Ingreso mediano alto","Otro"),"SLV":("El Salvador",LAC,"Ingreso mediano alto","Otro"),
"GTM":("Guatemala",LAC,"Ingreso mediano alto","Otro"),"HTI":("Haití",LAC,"Ingreso mediano bajo","Otro"),
"HND":("Honduras",LAC,"Ingreso mediano bajo","Otro"),"MEX":("México",LAC,"Ingreso mediano alto","Otro"),
"NIC":("Nicaragua",LAC,"Ingreso mediano bajo","Otro"),"PAN":("Panamá",LAC,"Ingreso alto","Otro"),
"PRY":("Paraguay",LAC,"Ingreso mediano alto","Otro"),"PER":("Perú",LAC,"Ingreso mediano alto","Otro"),
"URY":("Uruguay",LAC,"Ingreso alto","Otro"),"JAM":("Jamaica",LAC,"Ingreso mediano alto","Otro"),
"GUY":("Guyana",LAC,"Ingreso alto","Otro"),
"CAN":("Canadá",NAM,"Ingreso alto","Otro"),
"DEU":("Alemania",ECA,"Ingreso alto","Otro"),"ESP":("España",ECA,"Ingreso alto","Otro"),
"FRA":("Francia",ECA,"Ingreso alto","Otro"),"GBR":("Reino Unido",ECA,"Ingreso alto","Otro"),
"PRT":("Portugal",ECA,"Ingreso alto","Otro"),"NLD":("Países Bajos",ECA,"Ingreso alto","Otro"),
"CHE":("Suiza",ECA,"Ingreso alto","Otro"),"SWE":("Suecia",ECA,"Ingreso alto","Otro"),
"NOR":("Noruega",ECA,"Ingreso alto","Otro"),"IRL":("Irlanda",ECA,"Ingreso alto","Otro"),
"LUX":("Luxemburgo",ECA,"Ingreso alto","Otro"),"POL":("Polonia",ECA,"Ingreso alto","Otro"),
"HUN":("Hungría",ECA,"Ingreso alto","Otro"),"ROU":("Rumania",ECA,"Ingreso alto","Otro"),
"UKR":("Ucrania",ECA,"Ingreso mediano alto","Otro"),"RUS":("Rusia",ECA,"Ingreso alto","Otro"),
"SRB":("Serbia",ECA,"Ingreso mediano alto","Otro"),"BGR":("Bulgaria",ECA,"Ingreso alto","Otro"),
"KAZ":("Kazajistán",ECA,"Ingreso mediano alto","Otro"),"UZB":("Uzbekistán",ECA,"Ingreso mediano bajo","Otro"),
"TJK":("Tayikistán",ECA,"Ingreso mediano bajo","Otro"),"GEO":("Georgia",ECA,"Ingreso mediano alto","Otro"),
"TUR":("Turquía",ECA,"Ingreso mediano alto","Otro"),
"CHN":("China",EAP,"Ingreso mediano alto","Otro"),"KOR":("Corea del Sur",EAP,"Ingreso alto","Otro"),
"IDN":("Indonesia",EAP,"Ingreso mediano alto","Otro"),"PHL":("Filipinas",EAP,"Ingreso mediano alto","Otro"),
"VNM":("Vietnam",EAP,"Ingreso mediano alto","Otro"),"THA":("Tailandia",EAP,"Ingreso mediano alto","Otro"),
"MYS":("Malasia",EAP,"Ingreso mediano alto","Otro"),"SGP":("Singapur",EAP,"Ingreso alto","Otro"),
"MMR":("Myanmar",EAP,"Ingreso mediano bajo","Otro"),"KHM":("Camboya",EAP,"Ingreso mediano bajo","Otro"),
"MNG":("Mongolia",EAP,"Ingreso mediano alto","Otro"),"AUS":("Australia",EAP,"Ingreso alto","Otro"),
"NZL":("Nueva Zelanda",EAP,"Ingreso alto","Otro"),"PNG":("Papúa Nueva Guinea",EAP,"Ingreso mediano bajo","Otro"),
"IND":("India",SAS,"Ingreso mediano bajo","Otro"),"BGD":("Bangladés",SAS,"Ingreso mediano bajo","Otro"),
"NPL":("Nepal",SAS,"Ingreso mediano bajo","Otro"),"LKA":("Sri Lanka",SAS,"Ingreso mediano alto","Otro"),
"PAK":("Pakistán",MNA,"Ingreso mediano bajo","Otro"),"AFG":("Afganistán",MNA,"Ingreso bajo","Otro"),
"SAU":("Arabia Saudita",MNA,"Ingreso alto","Otro"),"ARE":("Emiratos Árabes Unidos",MNA,"Ingreso alto","Otro"),
"QAT":("Catar",MNA,"Ingreso alto","Otro"),"ISR":("Israel",MNA,"Ingreso alto","Otro"),
"IRN":("Irán",MNA,"Ingreso mediano alto","Otro"),"IRQ":("Irak",MNA,"Ingreso mediano alto","Otro"),
"EGY":("Egipto",MNA,"Ingreso mediano bajo","Otro"),"MAR":("Marruecos",MNA,"Ingreso mediano bajo","Otro"),
"DZA":("Argelia",MNA,"Ingreso mediano alto","Otro"),
"ZAF":("Sudáfrica",SSA,"Ingreso mediano alto","Otro"),"KEN":("Kenia",SSA,"Ingreso mediano bajo","Otro"),
"ETH":("Etiopía",SSA,"Ingreso bajo","Otro"),"GHA":("Ghana",SSA,"Ingreso mediano bajo","Otro"),
"SEN":("Senegal",SSA,"Ingreso mediano bajo","Otro"),"TZA":("Tanzania",SSA,"Ingreso mediano bajo","Otro"),
"RWA":("Ruanda",SSA,"Ingreso bajo","Otro"),"AGO":("Angola",SSA,"Ingreso mediano bajo","Otro"),
"COD":("R. D. del Congo",SSA,"Ingreso bajo","Otro"),"MDG":("Madagascar",SSA,"Ingreso bajo","Otro"),
"BWA":("Botsuana",SSA,"Ingreso mediano alto","Otro"),"SDN":("Sudán",SSA,"Ingreso bajo","Otro"),
}
rows = []
for iso, (n, r, i, g) in P.items():
    rows.append(dict(iso3=iso, pais=n, region=r, ingreso=i, grupo=g,
                     pib_pc_usd_2024=gdp[iso], esperanza_vida_2024=le[iso]))
df = pd.DataFrame(rows)
assert len(df) == 100 and df.notna().all().all()
df.sort_values("pais").to_csv("data/pib_esperanza_vida_2024.csv", index=False, encoding="utf-8")
print(len(df), "países guardados en data/pib_esperanza_vida_2024.csv")
