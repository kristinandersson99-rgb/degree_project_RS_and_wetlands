import xarray as xr
import numpy as np
import rasterio as rio
import matplotlib.pyplot as plt
import rioxarray as rxr
import os
import glob
import folium
import pandas as pd
import geopandas as gdp


def decode_bit(qa_arr: np.ndarray, bit: int) -> np.ndarray:
    """
    Source: https://code.usgs.gov/eros-user-services/processing_landsat_data/decoding-the-landsat-pixel-quality-assessment-band
    Decodes the QA Bit
        -   Args:
                qa_arr (np.ndarray): The quality assessment array.
                bit (int): The bit position to decode (0-15).
    
        -   Returns:
                np.ndarray: A boolean array where True indicates the presence of the specified condition.
    """
    return (qa_arr & 1 << bit) > 0


def qa_mask(qa_arr: np.ndarray, mask_type: str) -> np.ndarray:
    """
    Source: https://code.usgs.gov/eros-user-services/processing_landsat_data/decoding-the-landsat-pixel-quality-assessment-band
    Landsat QA Masking
    Creates a boolean mask based on the specified mask type.
     -   Args:
            qa_arr (np.ndarray): The quality assessment array.
            mask_type (str): The type of mask to create. Valid options are:
                "fill", "dilated", "cirrus", "cloud", "shadow", "snow", "clear", "water", 
                the high, mid and low masks refer to confidence levels.

     -   Returns:
            np.ndarray: The boolean mask with True and False values.
    """

    mask_type = mask_type.lower()  # Convert mask type to lowercase
    
    if mask_type == "fill":
        return decode_bit(qa_arr, 0)
    elif mask_type == "dilated":
        return decode_bit(qa_arr, 1)
    elif mask_type == "cirrus": 
        return decode_bit(qa_arr, 2) # Unused in Landsat 4-7
    elif mask_type == "cloud":
        return decode_bit(qa_arr, 3)
    elif mask_type == "shadow":
        return decode_bit(qa_arr, 4)
    elif mask_type == "snow":
        return decode_bit(qa_arr, 5)
    elif mask_type == "clear":
        return decode_bit(qa_arr, 6)
    elif mask_type == "water":
        return decode_bit(qa_arr, 7)
    elif mask_type == "high cloud":
        return decode_bit(qa_arr, 8) & decode_bit(qa_arr, 9) 
    elif mask_type == "mid cloud":
        return ~decode_bit(qa_arr, 8) & decode_bit(qa_arr, 9) 
    elif mask_type == "low cloud":
        return decode_bit(qa_arr, 8) & ~(decode_bit(qa_arr, 9)) 
    elif mask_type == "high shadow":
        return decode_bit(qa_arr, 10) & decode_bit(qa_arr, 11) 
    elif mask_type == "mid shadow":
        return ~decode_bit(qa_arr, 10) & decode_bit(qa_arr, 11) 
    elif mask_type == "low shadow":
        return decode_bit(qa_arr, 10) & ~decode_bit(qa_arr, 11) 
    elif mask_type == "high snow/ice":
        return decode_bit(qa_arr, 12) & decode_bit(qa_arr, 13) 
    elif mask_type == "mid snow/ice":
        return ~decode_bit(qa_arr, 12) & decode_bit(qa_arr, 13) 
    elif mask_type == "low snow/ice":
        return decode_bit(qa_arr, 12) & ~decode_bit(qa_arr, 13) # Unused in Landsat 4-7
    elif mask_type == "high cirrus":
        return decode_bit(qa_arr, 14) & decode_bit(qa_arr, 15) # Unused in Landsat 4-7
    elif mask_type == "mid cirrus":
        return ~decode_bit(qa_arr, 14) & decode_bit(qa_arr, 15) # Unused in Landsat 4-7
    elif mask_type == "low cirrus":
        return decode_bit(qa_arr, 14) & ~decode_bit(qa_arr, 15) # Unused in Landsat 4-7
    else:
        raise ValueError(f"Invalid mask type: {mask_type}")


def scl_mask(scl_arr: np.ndarray) -> np.ndarray:
    """
    Creates a boolean mask based on Sentinel-2 Scene Classification Layer (SCL).
    Returns True for pixels that should be masked (removed).

    Sources: 
    https://github.com/sentinel-hub/custom-scripts/blob/main/sentinel-2/cloud_statistics/script.js
    https://sentiwiki.copernicus.eu/web/s2-processing#S2-Processing-Scene-Classification

    SCL classes:
    0  = NO_DATA
    1  = SATURATED_OR_DEFECTIVE
    2  = CAST_SHADOWS
    3  = CLOUD_SHADOWS
    4  = VEGETATION
    5  = NOT_VEGETATED
    6  = WATER
    7  = UNCLASSIFIED
    8  = CLOUD_MEDIUM_PROBABILITY
    9  = CLOUD_HIGH_PROBABILITY
    10 = THIN_CIRRUS
    11 = SNOW_OR_ICE
    """
    classes_to_mask = [
        0,   # NO_DATA
        1,   # SATURATED_OR_DEFECTIVE
        2,   # CAST_SHADOWS
        3,   # CLOUD_SHADOWS
        8,   # CLOUD_MEDIUM_PROBABILITY
        9,   # CLOUD_HIGH_PROBABILITY
        10,  # THIN_CIRRUS
        11,  # SNOW_OR_ICE
    ]
    return np.isin(scl_arr, classes_to_mask)