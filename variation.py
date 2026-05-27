"""Variation-analys för indexraster - beräkna mean och std per år."""

import os
import glob
import pandas as pd
import rioxarray as rxr
import xarray as xr
import warnings
import numpy as np
import geopandas as gpd

from config import save_raster, build_analysis_output_dirs
warnings.filterwarnings("ignore", # Ignorera varning om std med 1 bild
                        message="Degrees of freedom <= 0 for slice",
                        category=RuntimeWarning)

def build_seasonal_stack(satellites, index_name, area, year, 
                          month_start=6, month_end=8, max_cloud=0):
	"""
	Bygger en stack med alla molnfria sommarbilder för ett specifikt år.
	
	Parametrar:
	-----------
	satellites  : dict
	    Satelliterar från build_analysis_satellites()
	index_name  : str
	    Namn på indexet (t.ex. "NDWI", "NDVI")
	area        : str
	    Studieområde (t.ex. "TAM")
	year        : int
	    År att hämta bilder för
	month_start : int
	    Startmånad (default: juni)
	month_end   : int
	    Slutmånad (default: augusti)
	max_cloud   : int
	    Max molntäckning (default: 0%)
	"""
	arrays = []
	dates  = []

	shape_gdf = None
	if area == "TAM":
		shape_path = r"D:\Masteruppsats\Studieomraden\Omr_polygon\TAM_lake.shp"
		if os.path.exists(shape_path):
			shape_gdf = gpd.read_file(shape_path)
		else:
			print(f"Varning: Shapefil {shape_path} hittades inte. Fortsätter utan att klippa.")

	for sat_name, sat in satellites.items():
		# Hitta alla filer för detta index och år
		pattern = os.path.join(
			sat["input"], index_name,
			f"*_{area}_{index_name}_CLD*.tif"
		)
		files = glob.glob(pattern)

		for f in files:
			# Extrahera datum och molntäckning från filnamnet
			basename = os.path.basename(f)
			
			# Extrahera datum från scennamnet
			date_token = basename.split("_")[2][:8]  # YYYYMMDD
			file_year  = int(date_token[:4])
			file_month = int(date_token[4:6])
			
			# Extrahera molntäckning
			cld_part = basename.split("_CLD")[1].replace(".tif", "")
			cloud_pct = int(cld_part)

			# Filtrera på år, månad och molntäckning
			if (file_year == year and 
				month_start <= file_month <= month_end and 
				cloud_pct <= max_cloud):
				
				arr = rxr.open_rasterio(f).squeeze("band", drop=True)
				# Klipp till studieområdet om shapefil finns, crs matchas automatiskt
				if shape_gdf is not None:
					if shape_gdf.crs != arr.rio.crs:
						shape_gdf = shape_gdf.to_crs(arr.rio.crs)
					# invert=True behåller pixlarna *utanför* polygonen och gör de innanför till NaN
					# drop=False ser till att rasterbildens ursprungliga utbredning (bounding box) behålls
					arr = arr.rio.clip(shape_gdf.geometry, arr.rio.crs, drop=False, invert=True)
				
				arrays.append(arr)
				dates.append(pd.Timestamp(f"{date_token[:4]}-{date_token[4:6]}-{date_token[6:8]}"))

	if not arrays:
		print(f"  Inga bilder hittades för {year}")
		return None

	print(f" {len(arrays)} bilder hittades för {year}")
	stack = xr.concat(arrays, dim=pd.DatetimeIndex(dates, name="time"))
	return stack


def build_and_save_variation_rasters(
	satellites,
	area,
	sensor,
	indices,
	years,
	month_start=6,
	month_end=8,
	max_cloud=0
):
	"""
	Bygger och sparar mean/std raster för specificerade index och år.
	
	Parametrar:
	-----------
	satellites : dict
	    Satelliter från build_analysis_satellites()
	area : str
	    Studieområde (t.ex. "TAM", "AM")
	sensor : str
	    Sensor ("landsat" eller "sentinel2")
	indices : list
	    Lista över index att bearbeta (t.ex. ["NDWI", "NDVI", "MNDWI", "NDMI"])
	years : list
	    Lista över år att bearbeta (t.ex. [2020, 2023, 2024, 2025])
	month_start : int
	    Startmånad (default: juni)
	month_end : int
	    Slutmånad (default: augusti)
	max_cloud : int
	    Max molntäckning i procent (default: 0%)
	"""
	
	# Hämta output-mappen för variation
	output_dirs = build_analysis_output_dirs(sensor=sensor)
	variation_dir = output_dirs["variation"]
	
	print(f"\n=== Variation-analys ===")
	print(f"Sensor: {sensor}")
	print(f"Område: {area}")
	print(f"Index: {indices}")
	print(f"År: {years}")
	print(f"Output-mapp: {variation_dir}\n")
	
	# Loop genom varje index
	for index_name in indices:
		print(f"Bearbetar {index_name}...")
		
		# Loop genom varje år
		for year in years:
			print(f"  År {year}...", end=" ")
			
			# Bygg seasonal stack för detta index och år
			seasonal_stack = build_seasonal_stack(
				satellites,
				index_name=index_name,
				area=area,
				year=year,
				month_start=month_start,
				month_end=month_end,
				max_cloud=max_cloud
			)
			
			if seasonal_stack is None:
				print("Inga bilder hittade.")
				continue

			# Kontrollera antal bilder
			n_images = len(seasonal_stack.time)

			# Spara alltid mean
			mean_data = seasonal_stack.mean(dim="time")
			mean_filename = f"{index_name}_{area}_{year}_mean.tif"
			save_raster(mean_data, variation_dir, mean_filename)

			# Spara std endast om det finns minst 2 bilder
			if n_images < 2:
				print(f"För få bilder ({n_images}) för std – sparar bara mean.")
				continue

			std_data = seasonal_stack.std(dim="time")
			std_filename = f"{index_name}_{area}_{year}_std.tif"
			save_raster(std_data, variation_dir, std_filename)

			print(f"{n_images} bilder → mean och std sparade.")
	
	print(f"\n✓ Variation-analys slutförd!\n")
