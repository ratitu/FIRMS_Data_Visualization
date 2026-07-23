"""UI components module for FIRMS Data Visualization."""

import pandas as pd
import streamlit as st
from typing import Optional

from config import (
    DATA_SOURCES,
    SOURCE_DISPLAY_NAMES,
    DEFAULT_COUNTRIES_ONLINE,
    DEFAULT_COUNTRIES_LOCAL,
    DEFAULT_BEGIN_YEAR,
    DEFAULT_END_YEAR,
    MIN_DATE,
    LOCAL_SOURCE,
    LOCAL_SOURCE_DISPLAY,
    DEFAULT_BBOX,
)
from data import get_countries, get_date_availability, check_map_key_status, FIRMSAPIError
from visualization import (
    create_date_line_chart, create_country_bar_chart,
    create_date_by_country_line_chart, create_fire_map,
    render_clicked_point, create_badge, create_badges,
    display_online_badges, display_local_badges,
)


def init_session_state() -> None:
    """Initialize session state variables."""
    defaults = {
        "source": DATA_SOURCES,
        "source_dict": SOURCE_DISPLAY_NAMES,
        "countries": pd.DataFrame(),
        "countries_dict": {},
        "data": pd.DataFrame(),
        "bbox_display": "",
        "date_display": "",
        "source_display": "",
        "date_range_display": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Load countries once
    if st.session_state.countries.empty:
        st.session_state.countries = get_countries()
        st.session_state.countries_dict = dict(
            zip(
                st.session_state.countries["abreviation"],
                st.session_state.countries["name"],
            )
        )


def render_online_sidebar() -> dict:
    """Render online mode sidebar and return user selections."""
    st.write("## Data Selection")

    bbox = st.text_input(
        label="Bounding Box (min_lon,min_lat,max_lon,max_lat)",
        value=DEFAULT_BBOX,
        help="Format: min_lon,min_lat,max_lon,max_lat (e.g., -85,-57,-32,14 for South America)",
    )

    source = st.selectbox(
        label="Source",
        options=st.session_state.source,
        index=2,  # MODIS_SP
        format_func=lambda x: st.session_state.source_dict[x],
    )

    date_range = st.slider(
        label="Date Range",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
        format="%d days",
        help="Begin from the date selected above",
    )

    map_key = st.text_input(
        label="FIRMS MAP_KEY",
        value=st.session_state.get("map_key", ""),
        type="password",
        help="Get a free API key from FIRMS",
    )

    col1, col2 = st.columns(2)
    with col1:
        check_mapkey = st.button(
            "Check MAP_KEY Status", help="Click to check your MAP_KEY status"
        )
    with col2:
        submit = st.button("Submit & Refresh", help="Click to get data", type="primary")

    if check_mapkey and map_key:
        status = check_map_key_status(map_key)
        if status is None:
            st.error("Failed to check MAP_KEY status")
        elif not status.get("valid", True):
            st.error("**Invalid MAP_KEY**")
        else:
            st.write(
                f"{status.get('current_transactions', 0)} / "
                f"{status.get('transaction_limit', 0)} in the past "
                f"{status.get('transaction_interval', 'unknown')}"
            )

    st.markdown(
        '<a href="https://firms.modaps.eosdis.nasa.gov/api/area/#mapKey" '
        'target="_blank">Apply FIRMS MAP_KEY for Free</a>',
        unsafe_allow_html=True,
    )

    # Date availability
    date_avail = get_date_availability(map_key, source)
    date = st.date_input(
        label="Date",
        value=pd.to_datetime(date_avail.get("max_date", MIN_DATE)),
        min_value=pd.to_datetime(date_avail.get("min_date", MIN_DATE)),
        max_value=pd.to_datetime(date_avail.get("max_date", MIN_DATE)),
    )

    return {
        "bbox": bbox,
        "source": source,
        "date_range": date_range,
        "date": date,
        "map_key": map_key,
        "submit": submit,
    }


def render_local_sidebar() -> dict:
    """Render local mode sidebar and return user selections."""
    st.write("## Data Selection")

    world = st.checkbox(
        label="The Whole World",
        value=False,
        help="Load data for all countries (will take a long time)",
    )

    if world:
        country_multi = st.session_state.countries["abreviation"].tolist()
        st.warning(
            "Warning! Data will be loaded country by country, it would take a long time!"
        )
    else:
        country_multi = st.multiselect(
            label="Country",
            options=st.session_state.countries["name"],
            help="Please do not select too many countries at once.",
            default=DEFAULT_COUNTRIES_LOCAL,
        )

    source = LOCAL_SOURCE
    st.selectbox(
        label="Source",
        options=[LOCAL_SOURCE],
        format_func=lambda x: LOCAL_SOURCE_DISPLAY,
        disabled=True,
    )

    year_begin = st.selectbox(
        label="Begin Year",
        options=list(range(2000, 2024)),
        index=DEFAULT_BEGIN_YEAR - 2000,
    )

    year_end = st.selectbox(
        label="End Year",
        options=list(range(2000, 2024)),
        index=DEFAULT_END_YEAR - 2000,
    )

    submit = st.button("Submit & Refresh", help="Click to get data", type="primary")

    return {
        "country_multi": country_multi,
        "source": source,
        "year_begin": year_begin,
        "year_end": year_end,
        "submit": submit,
        "world": world,
    }


def display_map(data: pd.DataFrame, highlight_point: tuple[float, float] | None = None) -> None:
    """Display the fire data on an interactive map with hover popups."""
    fig = create_fire_map(data, highlight_point=highlight_point)
    if fig:
        st.plotly_chart(
            fig,
            on_select="rerun",
            selection_mode="points",
            key="fire_map",
            width='stretch',
        )


def display_original_data_checkbox(data: pd.DataFrame, source_display: str) -> None:
    """Display original data checkbox and table."""
    if st.checkbox("Show Original Data", value=False):
        st.write("### Original Data")
        display_source_badge(source_display)
        st.dataframe(data, on_select="rerun", key="original_data_table")

        st.write(
            "[Attribute table for LANDSAT]"
            "(https://www.earthdata.nasa.gov/faq/firms-faq#ed-landsat-fires-attributes)"
        )
        st.write("[Attribute table for MODIS](https://go.nasa.gov/3JSgbdb)")
        st.write("[Attribute table for VIIRS](https://go.nasa.gov/3sf3ALb)")


def display_source_badge(source_display: str) -> None:
    """Display source/instrument badge."""
    from visualization import create_badge
    from config import BADGE_COLORS
    st.write(create_badge("Instrument", source_display, BADGE_COLORS["instrument"]))