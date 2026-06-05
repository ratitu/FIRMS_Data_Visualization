# FIRMS Data Visualization

[![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-370/)
[![Streamlit Version](https://img.shields.io/badge/streamlit-1.54.0-blue)](https://docs.streamlit.io/)
[![GPLv3 License](https://img.shields.io/github/license/hcy2206/FIRMS_Data_Visualization)](https://opensource.org/licenses/GPL-3.0)
[![NASA](https://img.shields.io/badge/Data%20Source-NASA%20FIRMS-red)](https://firms.modaps.eosdis.nasa.gov/)

## Introduction

Interactive visualization of global fire events using NASA FIRMS data. Filter by bounding box, date range, and satellite instrument. Click on fire points to view detailed attributes.

## Features

- **Bounding box selection** — draw or enter coordinates for any region
- **Multiple satellite instruments** — MODIS, VIIRS, LANDSAT
- **Interactive map** — hover for fire attributes (FRP, brightness, confidence), click for full details
- **Date range filtering** — 1–10 day windows
- **Local data mode** — load pre-downloaded CSV files
- **API request display** — shows the exact URL used for each query

## Data Source

[Fire Information for Resource Management System (FIRMS)](https://firms.modaps.eosdis.nasa.gov) data from NASA. Collected from [MODIS](https://modis.gsfc.nasa.gov/), [VIIRS](https://www.nesdis.noaa.gov/current-satellite-missions/currently-flying/joint-polar-satellite-system/visible-infrared-imaging) and [LANDSAT](https://landsat.gsfc.nasa.gov) satellite instruments via the [FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/).

## Setup

```bash
pip install -r requirements.txt
```

Optionally set your FIRMS MAP_KEY as an environment variable (or enter it in the UI):

```bash
export FIRMS_MAP_KEY="your_key_here"
```

[Get a free MAP_KEY](https://firms.modaps.eosdis.nasa.gov/api/area/#mapKey)

## Usage

```bash
streamlit run main.py
```

Select **Online** or **Local** mode in the sidebar. For online mode, enter a bounding box (default: South America `-85,-57,-32,14`), choose a source, date, and click **Submit & Refresh**.

## Project Structure

```
├── main.py            # Application entry point
├── config.py          # Constants and configuration
├── data.py            # API data fetching with error handling
├── ui.py              # Sidebar and UI components
├── visualization.py   # Charts and interactive map
├── requirements.txt
└── modis/             # Local data directory
```
