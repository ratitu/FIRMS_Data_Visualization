"""Data fetching module for FIRMS Data Visualization."""

import requests
import pandas as pd
from io import StringIO
from typing import Optional
import streamlit as st

from config import (
    FIRMS_BASE_URL,
    DEFAULT_MAP_KEY,
    MIN_DATE,
    DATA_SOURCES,
    SOURCE_DISPLAY_NAMES,
    LOCAL_SOURCE,
    CACHE_TTL,
    DEFAULT_BBOX,
)


class FIRMSAPIError(Exception):
    """Custom exception for FIRMS API errors."""

    pass


@st.cache_data(ttl=CACHE_TTL, show_spinner="Fetching data...")
def fetch_csv_data(url: str) -> pd.DataFrame:
    """Fetch CSV data from a URL and return as DataFrame."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.content.decode("utf-8")

        if "Invalid" in content or "<html>" in content.lower():
            raise FIRMSAPIError("Invalid response from API")

        return pd.read_csv(StringIO(content))
    except requests.RequestException as e:
        raise FIRMSAPIError(f"Request failed: {e}") from e
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL, show_spinner="Checking date availability...")
def get_date_availability(map_key: str, source: str) -> dict[str, str]:
    """Get available date range for a given source and map key."""
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    fallback = {"min_date": MIN_DATE, "max_date": today}

    if not map_key:
        return fallback

    url = f"{FIRMS_BASE_URL}/api/data_availability/csv/{map_key}/{source}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.content.decode("utf-8")

        if "Invalid" in content:
            return fallback

        lines = content.strip().split("\n")
        if len(lines) < 2:
            return fallback

        keys = lines[0].split(",")
        values = lines[1].split(",")
        return dict(zip(keys, values))
    except (requests.RequestException, IndexError, ValueError):
        return fallback


@st.cache_data(ttl=CACHE_TTL, show_spinner="Loading countries...")
def get_countries() -> pd.DataFrame:
    """Get list of countries from FIRMS API with fallback."""
    fallback_data = {
        "ABW": "Aruba",
        "AFG": "Afghanistan",
        "AGO": "Angola",
        "AIA": "Anguilla",
        "ALA": "Aland Islands",
        "ALB": "Albania",
        "AND": "Andorra",
        "ARE": "United Arab Emirates",
        "ARG": "Argentina",
        "ARM": "Armenia",
        "ASM": "American Samoa",
        "ATA": "Antarctica",
        "ATF": "French Southern Territories",
        "ATG": "Antigua and Barbuda",
        "AUS": "Australia",
        "AUT": "Austria",
        "AZE": "Azerbaijan",
        "BDI": "Burundi",
        "BEL": "Belgium",
        "BEN": "Benin",
        "BES": "Bonaire",
        "BFA": "Burkina Faso",
        "BGD": "Bangladesh",
        "BGR": "Bulgaria",
        "BHR": "Bahrain",
        "BHS": "Bahamas",
        "BIH": "Bosnia and Herzegovina",
        "BLM": "Saint Barthelemy",
        "BLR": "Belarus",
        "BLZ": "Belize",
        "BMU": "Bermuda",
        "BOL": "Bolivia",
        "BRA": "Brazil",
        "BRB": "Barbados",
        "BRN": "Brunei",
        "BTN": "Bhutan",
        "BWA": "Botswana",
        "CAF": "Central African Republic",
        "CAN": "Canada",
        "CHE": "Switzerland",
        "CHL": "Chile",
        "CHN": "China",
        "CIV": "Cote d'Ivoire",
        "CMR": "Cameroon",
        "COD": "Democratic Republic of the Congo",
        "COG": "Republic of the Congo",
        "COK": "Cook Islands",
        "COL": "Colombia",
        "COM": "Comoros",
        "CPV": "Cape Verde",
        "CRI": "Costa Rica",
        "CUB": "Cuba",
        "CUW": "Curacao",
        "CYM": "Cayman Islands",
        "CYP": "Cyprus",
        "CZE": "Czech Republic",
        "DEU": "Germany",
        "DJI": "Djibouti",
        "DMA": "Dominica",
        "DNK": "Denmark",
        "DOM": "Dominican Republic",
        "DZA": "Algeria",
        "ECU": "Ecuador",
        "EGY": "Egypt",
        "ERI": "Eritrea",
        "ESH": "Western Sahara",
        "ESP": "Spain",
        "EST": "Estonia",
        "ETH": "Ethiopia",
        "FIN": "Finland",
        "FJI": "Fiji",
        "FLK": "Falkland Islands",
        "FRA": "France",
        "FRO": "Faroe Islands",
        "FSM": "Micronesia",
        "GAB": "Gabon",
        "GBR": "United Kingdom",
        "GEO": "Georgia",
        "GGY": "Guernsey",
        "GHA": "Ghana",
        "GIB": "Gibraltar",
        "GIN": "Guinea",
        "GLP": "Guadeloupe",
        "GMB": "Gambia",
        "GNB": "Guinea-Bissau",
        "GNQ": "Equatorial Guinea",
        "GRC": "Greece",
        "GRD": "Grenada",
        "GRL": "Greenland",
        "GTM": "Guatemala",
        "GUF": "French Guiana",
        "GUM": "Guam",
        "GUY": "Guyana",
        "HKG": "Hong Kong",
        "HND": "Honduras",
        "HRV": "Croatia",
        "HTI": "Haiti",
        "HUN": "Hungary",
        "IDN": "Indonesia",
        "IMN": "Isle of Man",
        "IND": "India",
        "IRL": "Ireland",
        "IRN": "Iran",
        "IRQ": "Iraq",
        "ISL": "Iceland",
        "ISR": "Israel",
        "ITA": "Italy",
        "JAM": "Jamaica",
        "JEY": "Jersey",
        "JOR": "Jordan",
        "JPN": "Japan",
        "KAZ": "Kazakhstan",
        "KEN": "Kenya",
        "KGZ": "Kyrgyzstan",
        "KHM": "Cambodia",
        "KIR": "Kiribati",
        "KNA": "Saint Kitts and Nevis",
        "KOR": "South Korea",
        "KWT": "Kuwait",
        "LAO": "Laos",
        "LBN": "Lebanon",
        "LBR": "Liberia",
        "LBY": "Libya",
        "LCA": "Saint Lucia",
        "LIE": "Liechtenstein",
        "LKA": "Sri Lanka",
        "LSO": "Lesotho",
        "LTU": "Lithuania",
        "LUX": "Luxembourg",
        "LVA": "Latvia",
        "MAC": "Macau",
        "MAF": "Saint Martin",
        "MAR": "Morocco",
        "MDA": "Moldova",
        "MDG": "Madagascar",
        "MDV": "Maldives",
        "MEX": "Mexico",
        "MHL": "Marshall Islands",
        "MKD": "North Macedonia",
        "MLI": "Mali",
        "MLT": "Malta",
        "MMR": "Myanmar",
        "MNE": "Montenegro",
        "MNG": "Mongolia",
        "MNP": "Northern Mariana Islands",
        "MOZ": "Mozambique",
        "MRT": "Mauritania",
        "MSR": "Montserrat",
        "MTQ": "Martinique",
        "MUS": "Mauritius",
        "MWI": "Malawi",
        "MYS": "Malaysia",
        "MYT": "Mayotte",
        "NAM": "Namibia",
        "NCL": "New Caledonia",
        "NER": "Niger",
        "NFK": "Norfolk Island",
        "NGA": "Nigeria",
        "NIC": "Nicaragua",
        "NIU": "Niue",
        "NLD": "Netherlands",
        "NOR": "Norway",
        "NPL": "Nepal",
        "NRU": "Nauru",
        "NZL": "New Zealand",
        "OMN": "Oman",
        "PAK": "Pakistan",
        "PAN": "Panama",
        "PCN": "Pitcairn",
        "PER": "Peru",
        "PHL": "Philippines",
        "PLW": "Palau",
        "PNG": "Papua New Guinea",
        "POL": "Poland",
        "PRI": "Puerto Rico",
        "PRK": "North Korea",
        "PRT": "Portugal",
        "PRY": "Paraguay",
        "PSE": "Palestine",
        "PYF": "French Polynesia",
        "QAT": "Qatar",
        "REU": "Reunion",
        "ROU": "Romania",
        "RUS": "Russia",
        "RWA": "Rwanda",
        "SAU": "Saudi Arabia",
        "SDN": "Sudan",
        "SEN": "Senegal",
        "SGP": "Singapore",
        "SGS": "South Georgia",
        "SHN": "Saint Helena",
        "SJM": "Svalbard",
        "SLB": "Solomon Islands",
        "SLE": "Sierra Leone",
        "SLV": "El Salvador",
        "SMR": "San Marino",
        "SOM": "Somalia",
        "SPM": "Saint Pierre and Miquelon",
        "SRB": "Serbia",
        "SSD": "South Sudan",
        "STP": "Sao Tome and Principe",
        "SUR": "Suriname",
        "SVK": "Slovakia",
        "SVN": "Slovenia",
        "SWE": "Sweden",
        "SWZ": "Eswatini",
        "SXM": "Sint Maarten",
        "SYC": "Seychelles",
        "SYR": "Syria",
        "TCA": "Turks and Caicos Islands",
        "TCD": "Chad",
        "TGO": "Togo",
        "THA": "Thailand",
        "TJK": "Tajikistan",
        "TKL": "Tokelau",
        "TKM": "Turkmenistan",
        "TLS": "Timor-Leste",
        "TON": "Tonga",
        "TTO": "Trinidad and Tobago",
        "TUN": "Tunisia",
        "TUR": "Turkey",
        "TUV": "Tuvalu",
        "TWN": "Taiwan",
        "TZA": "Tanzania",
        "UGA": "Uganda",
        "UKR": "Ukraine",
        "URY": "Uruguay",
        "USA": "United States",
        "UZB": "Uzbekistan",
        "VAT": "Vatican City",
        "VCT": "Saint Vincent and the Grenadines",
        "VEN": "Venezuela",
        "VGB": "British Virgin Islands",
        "VIR": "US Virgin Islands",
        "VNM": "Vietnam",
        "VUT": "Vanuatu",
        "WLF": "Wallis and Futuna",
        "WSM": "Samoa",
        "YEM": "Yemen",
        "ZAF": "South Africa",
        "ZMB": "Zambia",
        "ZWE": "Zimbabwe",
    }

    try:
        response = requests.get(
            f"{FIRMS_BASE_URL}/api/countries", timeout=10
        )
        if response.status_code == 200 and "Invalid" not in response.text:
            countries_df = pd.read_csv(StringIO(response.text), sep=";")
            if "name" in countries_df.columns:
                return countries_df.sort_values("name").reset_index(drop=True)
    except Exception:
        pass

    # Fallback
    df = pd.DataFrame(list(fallback_data.items()), columns=["abreviation", "name"])
    df.insert(0, "id", range(1, len(df) + 1))
    return df.sort_values("name").reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL)
def fetch_online_data(
    map_key: str, source: str, bbox: str, date_range: int, date: str
) -> tuple[pd.DataFrame, str]:
    """Fetch fire data from FIRMS API for given bounding box and date range."""
    if not map_key:
        raise FIRMSAPIError("MAP_KEY is required for online data")

    url = (
        f"{FIRMS_BASE_URL}/api/area/csv/{map_key}/{source}/{bbox}/"
        f"{date_range}/{date}"
    )

    data = fetch_csv_data(url)

    # Filter out HTML error rows if any
    if "<html>" in data.columns:
        data = data[data["<html>"].isnull()]

    return data, url


@st.cache_data(ttl=CACHE_TTL)
def load_local_data(year: int, country: str) -> pd.DataFrame:
    """Load local MODIS data for a specific year and country."""
    country_safe = country.replace(" ", "_").replace("'", "_")
    path = f"{LOCAL_SOURCE}/{year}/{LOCAL_SOURCE}_{year}_{country_safe}.csv"

    try:
        data = pd.read_csv(path)
        data["country"] = country
    except FileNotFoundError:
        data = pd.read_csv("modis/modis_empty.csv")
        data["country"] = ""

    return data


def collect_local_data(
    year_begin: int, year_end: int, countries: list[str]
) -> pd.DataFrame:
    """Collect local data for multiple countries and years."""
    empty_df = pd.read_csv("modis/modis_empty.csv")
    empty_df["country"] = ""

    all_data = [empty_df]

    for country in countries:
        for year in range(year_begin, year_end + 1):
            all_data.append(load_local_data(year, country))

    return pd.concat(all_data, ignore_index=True)


def check_map_key_status(map_key: str) -> Optional[dict]:
    """Check the status of a FIRMS MAP_KEY."""
    if not map_key:
        return None

    try:
        response = requests.get(
            f"{FIRMS_BASE_URL}/mapserver/mapkey_status/?MAP_KEY={map_key}",
            timeout=10,
        )
        if response.content == b"MAP_KEY is invalid or your have exceeded your transaction/time limit. Please try again later.":
            return {"valid": False}
        return response.json()
    except requests.RequestException:
        return None


def validate_date_range(begin_year: int, end_year: int) -> bool:
    """Validate that begin year is not after end year."""
    return begin_year <= end_year