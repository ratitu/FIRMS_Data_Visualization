"""Configuration and constants for FIRMS Data Visualization."""

import os
from typing import Final

# API Configuration
FIRMS_BASE_URL: Final[str] = "https://firms.modaps.eosdis.nasa.gov"
DEFAULT_MAP_KEY: Final[str] = os.getenv("FIRMS_MAP_KEY", "")

# Data Sources
DATA_SOURCES: Final[list[str]] = [
    "LANDSAT_NRT",
    "MODIS_NRT",
    "MODIS_SP",
    "VIIRS_NOAA20_NRT",
    "VIIRS_SNPP_NRT",
    "VIIRS_SNPP_SP",
]

SOURCE_DISPLAY_NAMES: Final[dict[str, str]] = {
    "LANDSAT_NRT": "LANDSAT (NRT) [US/Canada only]",
    "MODIS_NRT": "MODIS (URT+NRT)",
    "MODIS_SP": "MODIS (SP)",
    "VIIRS_NOAA20_NRT": "VIIRS NOAA-20 (URT+NRT)",
    "VIIRS_SNPP_NRT": "VIIRS S-NPP (URT+NRT)",
    "VIIRS_SNPP_SP": "VIIRS S-NPP (SP)",
}

# Local data source
LOCAL_SOURCE: Final[str] = "modis"
LOCAL_SOURCE_DISPLAY: Final[str] = "MODIS (SP)"

# Date Configuration
MIN_DATE: Final[str] = "2000-11-01"
DEFAULT_BEGIN_YEAR: Final[int] = 2020
DEFAULT_END_YEAR: Final[int] = 2022

# Default countries
DEFAULT_COUNTRIES_ONLINE: Final[list[str]] = ["CHN", "USA"]
DEFAULT_COUNTRIES_LOCAL: Final[list[str]] = ["China", "United States"]

# Default bounding box (South America): min_lon, min_lat, max_lon, max_lat
DEFAULT_BBOX: Final[str] = "-85,-57,-32,14"

# Cache TTL (in seconds)
CACHE_TTL: Final[int] = 3600

# UI Configuration
PAGE_TITLE: Final[str] = "FIRMS Data Visualization"
PAGE_ICON: Final[str] = "https://markdown-tuchuang-hcy2206.oss-cn-shanghai.aliyuncs.com/img/202306151943857.png"
GITHUB_URL: Final[str] = "https://github.com/hcy2206/FIRMS_Data_Visualization.git"

# Badge colors
BADGE_COLORS: Final[dict[str, str]] = {
    "country": "blue",
    "date": "brightgreen",
    "date_range": "yellow",
    "years": "brightgreen",
    "instrument": "yellowgreen",
}