"""Delad konfiguration för notebooks i Masteruppsats-projektet."""


import os

LANDSAT_ROOT = r"D:\Masteruppsats\Landsat"
SENTINEL_ROOT = r"D:\Masteruppsats\Sentinel"
REF_AREAS = {"TAM", "AM"}


def _normalize_sensor(sensor):
	sensor_norm = sensor.lower()
	if sensor_norm in {"sentinel", "sentinel2", "s2"}:
		return "sentinel2"
	if sensor_norm in {"landsat", "ls"}:
		return "landsat"
	raise ValueError(f"Okand sensor: {sensor}. Tillatna varden: 'landsat' eller 'sentinel2'.")


def build_analysis_output_dirs(sensor="landsat"):
	"""
	Returnerar output-mappar for analysnotebookar per sensor.
	
	"""
	sensor_norm = _normalize_sensor(sensor)

	if sensor_norm == "sentinel2":
		theil_sen_dir = rf"{SENTINEL_ROOT}\theil_sen"
		theil_sen_vizual_dir = rf"{SENTINEL_ROOT}\theil_sen_mk_84_24"
		change_dir = rf"{SENTINEL_ROOT}\change_images"
		climate_dir = rf"{SENTINEL_ROOT}\climate_data"
		variation_dir = rf"{SENTINEL_ROOT}\variation"
		AHP_dir = rf"{SENTINEL_ROOT}\AHP"
	else:
		theil_sen_dir = rf"{LANDSAT_ROOT}\theil_sen_mk"
		theil_sen_vizual_dir = rf"{LANDSAT_ROOT}\theil_sen_mk_84_24"
		change_dir = rf"{LANDSAT_ROOT}\change_images"
		climate_dir = rf"{LANDSAT_ROOT}\climate_data"
		variation_dir = rf"{LANDSAT_ROOT}\variation"
		AHP_dir = rf"{LANDSAT_ROOT}\AHP"


	return {
		"theil_sen_mk": theil_sen_dir,
		"theil_sen": theil_sen_dir,
		"theil_sen_vizualization": theil_sen_vizual_dir,
		"change_images": change_dir,
		"climate_data": climate_dir,
		"variation": variation_dir,
		"AHP": AHP_dir,
	}


# Bakatkompatibel default for befintliga notebooks
ANALYSIS_OUTPUT_DIRS = build_analysis_output_dirs("landsat")


STUDY_AREAS_ROOT = r"D:\Masteruppsats\Studieomraden"

STUDY_AREA_PATHS = {
	"GRM": rf"{STUDY_AREAS_ROOT}\Omr_polygon\Grundsjomossarna.shp",
	"GM": rf"{STUDY_AREAS_ROOT}\Omr_polygon\Gunnarsmaren.shp",
	"LF": rf"{STUDY_AREAS_ROOT}\Omr_polygon\Lovfjarden.shp",
	"AM": rf"{STUDY_AREAS_ROOT}\Omr_polygon\Ambricka_DoNotUse.shp",
	"TAM": rf"{STUDY_AREAS_ROOT}\Omr_polygon\Tangsamurarna.shp",
	"GS": rf"{STUDY_AREAS_ROOT}\Omr_polygon\Grundsjon.shp",
}

# Open wetland area polygons
OPEN_WETLAND_AREA = {
	"GRM_wetland": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_GRM_final.shp",
	"GM_wetland": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_GM_final.shp",
	"LF_wetland": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_LF_final.shp",
	"AM_wetland": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_AM_final.shp",
	"TAM_wetland": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_TAM_final.shp",
	"GS_wetland": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_GS_final.shp",
	
	"GRM_wetland_east": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_GRM_east_final.shp",
	"GRM_wetland_west": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_GRM_west_final.shp",
	"LF_wetland_east": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_LF_east_final.shp",
	"LF_wetland_west": rf"{STUDY_AREAS_ROOT}\open_wetland_polygon\open_wetland_LF_west_final.shp",
}

SEA_POLYGON_PATH = rf"{STUDY_AREAS_ROOT}\Gunnarsmaren\Vektor\Mark\hav.shp"


PREPROCESS_BANDS = {
	"L05": {"blue": "SR_B1", "green": "SR_B2", "red": "SR_B3", "nir": "SR_B4", "swir": "SR_B5"},
	"L07": {"blue": "SR_B1", "green": "SR_B2", "red": "SR_B3", "nir": "SR_B4", "swir": "SR_B5"},
	"L0809": {"blue": "SR_B2", "green": "SR_B3", "red": "SR_B4", "nir": "SR_B5", "swir": "SR_B6"},
	"S2": {"blue": "B02", "green": "B03", "red": "B04", "nir": "B8A", "swir": "B11", "scl": "SCL"}, # Kom ihåg att jag använder 8A för NDVI!
}


def build_analysis_satellites(area, sensor="landsat"):
	"""Returnerar input-mappar for analysnotebookar (processed data) per sensor."""
	sensor_norm = _normalize_sensor(sensor)

	if sensor_norm == "sentinel2":
		prefix = "reference" if area in REF_AREAS else "object"
		return {
			"S2": {
				"input": rf"{SENTINEL_ROOT}\{prefix}_processed",
				"sensor": "sentinel2",
			},
		}

	prefix = "Ref_Landsat" if area in REF_AREAS else "Landsat"
	return {
		"L05": {"input": rf"{LANDSAT_ROOT}\{prefix}_05_processed", "sensor": "landsat"},
		"L07": {"input": rf"{LANDSAT_ROOT}\{prefix}_07_processed", "sensor": "landsat"},
		"L0809": {"input": rf"{LANDSAT_ROOT}\{prefix}_0809_processed", "sensor": "landsat"},
	}


def build_preprocessing_satellites(area, sensor="landsat"):
	"""Returnerar input/output-mappar och banddefinitioner for preprocessing per sensor."""
	sensor_norm = _normalize_sensor(sensor)

	if sensor_norm == "sentinel2":
		prefix = "reference" if area in REF_AREAS else "object"
		return {
			"S2": {
				"input": rf"{SENTINEL_ROOT}\{prefix}",
				"output": rf"{SENTINEL_ROOT}\{prefix}_processed",
				"bands": PREPROCESS_BANDS["S2"],
				"sensor": "sentinel2",
			},
		}

	prefix = "Ref_Landsat" if area in REF_AREAS else "Landsat"
	return {
		"L05": {
			"input": rf"{LANDSAT_ROOT}\{prefix}_05",
			"output": rf"{LANDSAT_ROOT}\{prefix}_05_processed",
			"bands": PREPROCESS_BANDS["L05"],
			"sensor": "landsat",
		},
		"L07": {
			"input": rf"{LANDSAT_ROOT}\{prefix}_07",
			"output": rf"{LANDSAT_ROOT}\{prefix}_07_processed",
			"bands": PREPROCESS_BANDS["L07"],
			"sensor": "landsat",
		},
		"L0809": {
			"input": rf"{LANDSAT_ROOT}\{prefix}_0809",
			"output": rf"{LANDSAT_ROOT}\{prefix}_0809_processed",
			"bands": PREPROCESS_BANDS["L0809"],
			"sensor": "landsat",
		},
	}


def print_satellite_setup(area, satellites, sensor="landsat"):
	"""Skriver ut vald area, sensor och vilka satellitmappar som används."""
	map_type = "referens" if area in REF_AREAS else "standard"
	sensor_norm = _normalize_sensor(sensor)
	print(f"Studieområde: {area}")
	print(f"Anvander {map_type}-mappar for {sensor_norm}")
	for sat_name, sat in satellites.items():
		print(f"  {sat_name}: {sat['input']}")


def load_and_prepare_scene_logs(satellites, area):
	"""Läser in och kombinerar scenloggar för alla satelliter."""
	import os
	import pandas as pd

	logs = []
	for sat_name, sat in satellites.items():
		log_path = os.path.join(sat["input"], f"scene_log_{area}.csv")
		df = pd.read_csv(log_path)
		df["sat_name"] = sat_name
		df["output_dir"] = sat["input"]
		logs.append(df)

	log = pd.concat(logs).reset_index(drop=True)
	log["date"] = pd.to_datetime(log[["year", "month", "day"]])
	log["days_from_july15"] = log.groupby("year")["date"].transform(
		lambda d: (d - pd.Timestamp(f"{d.dt.year.iloc[0]}-07-15")).dt.days.abs()
	)
	return log


def prioritize_scene(df_year):
	"""
	Prioriterar molnfria scener enligt följande:
	1. 20 juni - 15 aug (narmast 15 juli)
	2. 16-31 aug (narmast 15 juli)
	3. 1-19 juni (narmast 15 juli)
	Returnerar den valda scenen eller None om ingen molnfri scen finns.
	"""
	clean = df_year[df_year["cloud_pct"] == 0].copy()
	if clean.empty:
		return None

	mmdd = clean["date"].dt.month * 100 + clean["date"].dt.day
	clean = clean[(mmdd >= 601) & (mmdd <= 831)]
	if clean.empty:
		return None

	pref = clean[
		(clean["date"].dt.month * 100 + clean["date"].dt.day >= 620) &
		(clean["date"].dt.month * 100 + clean["date"].dt.day <= 815)
	]
	if not pref.empty:
		return pref.loc[pref["days_from_july15"].idxmin()]

	aug = clean[(clean["date"].dt.month == 8) & (clean["date"].dt.day > 15)]
	if not aug.empty:
		return aug.loc[aug["days_from_july15"].idxmin()]

	jun = clean[(clean["date"].dt.month == 6) & (clean["date"].dt.day < 20)]
	if not jun.empty:
		return jun.loc[jun["days_from_july15"].idxmin()]

	return None


def select_best_scenes(log):
	"""Valjer en bast prioriterad molnfri scen per ar."""
	return (
		log.groupby("year")
		.apply(prioritize_scene)
		.dropna()
		.reset_index(drop=False)
	)


def build_stack(best_scenes, index_name, area):
	"""Bygger en tidsstack (xarray DataArray) for ett index."""
	import glob
	import os
	import pandas as pd
	import rioxarray as rxr
	import xarray as xr

	arrays = []
	dates = []

	for _, row in best_scenes.iterrows():
		pattern = os.path.join(
			row["output_dir"], index_name,
			f"*{row['scene_name']}*_{area}_{index_name}_CLD*.tif"
		)
		files = glob.glob(pattern)
		if not files:
			print(f"  Varning: Ingen fil hittad for {row['scene_name']}")
			continue

		arr = rxr.open_rasterio(files[0]).squeeze("band", drop=True)
		arrays.append(arr)
		dates.append(row["date"])

	stack = xr.concat(arrays, dim=pd.DatetimeIndex(dates, name="time"))
	return stack


def save_raster(data_array, output_path, filename):
    """
    Sparar en xarray DataArray som GeoTIFF-fil med georeferencing bevarat.
    """
    import os
    import numpy as np
    import rasterio
    
    os.makedirs(output_path, exist_ok=True)
    filepath = os.path.join(output_path, filename)
    
    try:
        # Radera gammal fil helt - med felhantering för låsta filer
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except PermissionError:
                print(f"  VARNING: Kunde inte radera gammal fil (låst): {filepath}")
                print(f"           Försöker skriva över den...")
        
        # Konvertera data till numpy array
        data = np.array(data_array.values, dtype=np.float32)
        
        # Ensure 2D
        if data.ndim > 2:
            data = data.squeeze()
        
        height, width = data.shape
        
        # Hämta CRS och transform från data_array
        crs = data_array.rio.crs if hasattr(data_array.rio, 'crs') else None
        transform = data_array.rio.transform() if hasattr(data_array.rio, 'transform') else None
        
        # Spara fil EXPLICIT med rasterio
        with rasterio.open(
            filepath,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=rasterio.float32,
            crs=crs,
            transform=transform,
        ) as dst:
            dst.write(data, 1)
        
        # Verifiera
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"Sparad: {filepath} ({file_size} bytes)")
        else:
            print(f"FEL: Filen sparades inte!")
            
    except Exception as e:
        print(f"FEL vid sparning av {filename}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def select_all_clear_scenes(log, month_start=6, month_end=8):
	"""
	Väljer alla molnfria scener inom sommarsäsongen per år.
	Returnerar en DataFrame med alla valda scener.
	
	Parametrar:
	-----------
	log : DataFrame
	    Scenlogg från load_and_prepare_scene_logs()
	month_start : int
	    Startmånad (default: juni)
	month_end : int
	    Slutmånad (default: augusti)
	"""
	# Filtrera på molnfria scener inom sommarsäsongen
	mmdd = log["date"].dt.month * 100 + log["date"].dt.day
	
	clear = log[
		(log["cloud_pct"] == 0) &
		(mmdd >= month_start * 100 + 15) &
		(mmdd <= month_end * 100 + 31)
	].copy()
	
	return clear.reset_index(drop=True)


def build_mean_stack(all_clear_scenes, index_name, area):
	"""
	Bygger en tidsstack med medelvärde per år av alla molnfria sommarscener.
	Om bara en scen finns för ett år används den direkt.
	
	Parametrar:
	-----------
	all_clear_scenes : DataFrame
	    Alla molnfria scener från select_all_clear_scenes()
	index_name : str
	    Namn på indexet (t.ex. "NDVI")
	area : str
	    Studieområde (t.ex. "GRM")
	"""
	import glob
	import os
	import pandas as pd
	import numpy as np
	import rioxarray as rxr
	import xarray as xr

	yearly_arrays = []
	yearly_dates  = []

	for year, year_df in all_clear_scenes.groupby(all_clear_scenes["date"].dt.year):
		scene_arrays = []

		for _, row in year_df.iterrows():
			pattern = os.path.join(
				row["output_dir"], index_name,
				f"*{row['scene_name']}*_{area}_{index_name}_CLD*.tif"
			)
			files = glob.glob(pattern)
			if not files:
				print(f"  Varning: Ingen fil hittad för {row['scene_name']}")
				continue

			arr = rxr.open_rasterio(files[0]).squeeze("band", drop=True)
			scene_arrays.append(arr)

		if not scene_arrays:
			print(f"  Varning: Inga filer hittades för år {year}")
			continue

		if len(scene_arrays) == 1:
			# Bara en scen – använd direkt
			year_mean = scene_arrays[0]
			print(f"  {year}: 1 scen (används direkt)")
		else:
			# Flera scener – beräkna medelvärde
			year_stack = xr.concat(scene_arrays, dim="scene")
			year_mean  = year_stack.mean(dim="scene", skipna=True)
			print(f"  {year}: {len(scene_arrays)} scener → medelvärde beräknat")

		yearly_arrays.append(year_mean)
		yearly_dates.append(pd.Timestamp(f"{year}-07-15"))  # Representativt datum

	if not yearly_arrays:
		raise ValueError(f"Inga bilder hittades för {area} {index_name}")

	stack = xr.concat(yearly_arrays, dim=pd.DatetimeIndex(yearly_dates, name="time"))
	return stack


def select_scenes_hybrid(log, period_start=1984, period_end=1989):
    """
    Väljer ALLA molnfria scener för period_start-period_end,
    och bara BÄSTA scen per år för resterande år.
    """
    import pandas as pd
    
    # Dela upp loggen
    early_period = log[log["year"].between(period_start, period_end)].copy()
    other_years = log[~log["year"].between(period_start, period_end)].copy()
    
    # Använd båda strategier
    selected_early = select_all_clear_scenes(early_period)
    selected_other = select_best_scenes(other_years)
    
    # Kombinera och sortera
    combined = pd.concat([selected_early, selected_other], ignore_index=True)
    return combined.sort_values("date").reset_index(drop=True)