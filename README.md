# Fjärranalys-pipeline

Masteruppsats i fjärranalys med fokus på våtmarker.
Projektet använder Landsat- och Sentinel-2-data för att beräkna ett *Wetland Health Index* 
och utföra en trendanalys samt image differencing baserat på spektrala index.

---

## Projektstruktur

```
projekt/
│
├── config.py                           # Gemensam konfiguration: sökvägar, satellitinställningar, hjälpfunktioner
├── preprocessing.py                    # QA-maskering (Landsat pixel-QA och Sentinel-2 SCL)
├── variation.py                        # Beräknar mean- och std-raster per år och index
├── climate.py                          # SMHI-datahantering och klimatanomalier
│
├── preprocessing.ipynb                 # Förbehandling av rådata (bandberäkning, klippning)
├── WHI_part1_preparing_rasters.ipynb   # Steg 1: Bygger mean/std-raster inför WHI-beräkning
├── WHI_part2.ipynb                     # Steg 2: Min-max-normalisering och AHP-viktning
├── WHI_part3.ipynb                     # Steg 3: Klassificering, AHP-viktning och WHI-kartor
├── theil_sen_main.ipynb                # Trendanalys: Theil-Sen + Mann-Kendall (1984–2024)
├── change_detection.ipynb              # Bildifferensiering, t.ex. restaureringseffekter 2025
├── climate.ipynb                       # Klimatanomalier mot normalperioden 1991–2020
└── mean_vals_correlation.ipynb         # Korrelationsanalys och medelvärden inom öppen våtmark
```

---

## Körordning

Kör notebooks i följande ordning för ett nytt studieområde:

```
1. preprocessing.ipynb
      ↓
2. WHI_part1_preparing_rasters.ipynb
      ↓
3. WHI_part2.ipynb
      ↓
4. WHI_part3.ipynb
```

Övriga notebooks kan köras fristående efter att preprocessingen är klar:

- `theil_sen_main.ipynb` – trendanalys, kräver processade scener
- `change_detection.ipynb` – bildifferensiering, kräver processade scener
- `climate.ipynb` – kräver SMHI-datafiler
- `mean_vals_correlation.ipynb` – kräver färdiga variation-raster

---

## Konfiguration

### Ange studieområde och sensor

I varje notebook finns två variabler längst upp som du behöver anpassa:

```python
area   = "GRM"        # Välj studieområde
sensor = "landsat"    # "landsat" eller "sentinel2"
```

### Sökvägar

Absoluta sökvägar är samlade i `config.py`.

Flyttas projektet, justera `LANDSAT_ROOT`, `SENTINEL_ROOT` och `STUDY_AREAS_ROOT` i `config.py`.

---

## Python-miljö

Projektet använder miljön `thesis_env` med Python 3.11.

### Viktiga paket

```
rioxarray
xarray
rasterio
geopandas
numpy
pandas
matplotlib
pymannkendall
scipy
openpyxl
```

### Installera beroenden

```bash
pip install rioxarray xarray rasterio geopandas numpy pandas matplotlib pymannkendall scipy openpyxl
```

---

## .gitignore

```
__pycache__/
*.pyc
.vscode/
*.tif
*.shp
*.dbf
*.shx
*.prj
*.cpg
```
