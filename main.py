"""FIRMS Data Visualization - Main Application."""

import pandas as pd
import streamlit as st

from config import (
    PAGE_TITLE,
    PAGE_ICON,
    GITHUB_URL,
    BADGE_COLORS,
)
from data import (
    fetch_online_data,
    collect_local_data,
    validate_date_range,
    FIRMSAPIError,
)
from ui import (
    init_session_state,
    render_online_sidebar,
    render_local_sidebar,
    display_map,
    display_original_data_checkbox,
)
from visualization import (
    create_date_line_chart,
    create_country_bar_chart,
    create_date_by_country_line_chart,
    create_badge,
    render_clicked_point,
    display_local_badges,
    display_source_badge,
)


def _handle_online_submit(selections: dict) -> None:
    """Handle online data fetch submission."""
    bbox = selections["bbox"]
    source = selections["source"]
    date_range = selections["date_range"]
    date = selections["date"]
    map_key = selections["map_key"]

    if not map_key:
        st.error("Please enter a valid FIRMS MAP_KEY")
        return

    if not bbox:
        st.error("Please enter a bounding box")
        return

    try:
        with st.spinner("Fetching data from FIRMS API..."):
            data, api_url = fetch_online_data(map_key, source, bbox, date_range, str(date))

        st.session_state.data = data
        st.session_state.api_url = api_url
        st.session_state.bbox_display = bbox.replace(",", ", ")
        st.session_state.date_display = str(date).replace("-", "--")
        st.session_state.source_display = st.session_state.source_dict[source].replace(
            " ", "%20"
        )
        st.session_state.date_range_display = f"{date_range}%20days"
        st.session_state.map_key = map_key

        st.success(f"Loaded {len(data)} fire records")
    except FIRMSAPIError as e:
        st.error(f"Failed to fetch data: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


def _handle_local_submit(selections: dict) -> None:
    """Handle local data load submission."""
    country_multi = selections["country_multi"]
    year_begin = selections["year_begin"]
    year_end = selections["year_end"]

    if not validate_date_range(year_begin, year_end):
        st.error("Begin year should be earlier than end year!")
        return

    if not country_multi:
        st.error("Please select at least one country")
        return

    try:
        with st.spinner("Loading local data..."):
            data = collect_local_data(year_begin, year_end, country_multi)

        st.session_state.data = data
        st.success(f"Loaded {len(data)} fire records")
    except Exception as e:
        st.error(f"Failed to load data: {e}")


st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    initial_sidebar_state="auto",
    menu_items={
        "About": (
            "This is a world wide fire events data visualization project based "
            "on Streamlit by Python, data provided by NASA FIRMS.\n\n"
            f"Github Repository: {GITHUB_URL}"
        )
    },
    layout="wide",
)

init_session_state()

st.markdown("## Fire Information for Resource Management System")
st.markdown("# Worldwide Fire Data Visualization")

# Sidebar - Mode Selection
with st.sidebar:
    st.write("## Mode Selection")
    online = st.selectbox(
        label="Select data source",
        options=[True, False],
        format_func=lambda x: "Online" if x else "Local",
        index=0,
    )

# Render appropriate sidebar based on mode
if online:
    selections = render_online_sidebar()
else:
    selections = render_local_sidebar()

# Handle form submission
if selections.get("submit"):
    if online:
        _handle_online_submit(selections)
    else:
        _handle_local_submit(selections)


# Main content area
data = st.session_state.data

# Check for table row selection (from original data dataframe)
highlight_point = None
table_sel = st.session_state.get("original_data_table")
if table_sel and table_sel.get("selection"):
    sel_rows = table_sel["selection"].get("rows", [])
    if sel_rows:
        selected = data.iloc[sel_rows[0]]
        if "latitude" in selected.index and "longitude" in selected.index:
            highlight_point = (selected["latitude"], selected["longitude"])

if not data.empty:
    # Map
    st.write("### Fire Events Map")
    if online:
        st.write(create_badge("Bounding Box", st.session_state.bbox_display, BADGE_COLORS["country"]))
    else:
        display_local_badges(
            selections.get("year_begin", 2000),
            selections.get("year_end", 2022),
            selections.get("country_multi", []),
        )
    display_map(data, highlight_point=highlight_point)
    render_clicked_point(data)

    # Date line chart
    date_line = create_date_line_chart(data)
    if date_line:
        st.write("### Count by Date")
        if online:
            st.write(create_badge("Bounding Box", st.session_state.bbox_display, BADGE_COLORS["country"]))
        st.plotly_chart(date_line, width='stretch')

    # Date by country line chart (for local mode with multiple countries)
    if not online and len(selections.get("country_multi", [])) >= 2:
        date_country_line = create_date_by_country_line_chart(data)
        if date_country_line:
            st.write("### Count by Date (by Country)")
            display_local_badges(
                selections.get("year_begin", 2000),
                selections.get("year_end", 2022),
                selections.get("country_multi", []),
            )
            st.plotly_chart(date_country_line, width='stretch')

    # Country bar chart
    country_bar = create_country_bar_chart(data, st.session_state.countries_dict)
    if country_bar:
        st.write("### Count by Country")
        if online:
            st.write(create_badge("Bounding Box", st.session_state.bbox_display, BADGE_COLORS["country"]))
        else:
            display_local_badges(
                selections.get("year_begin", 2000),
                selections.get("year_end", 2022),
                selections.get("country_multi", []),
            )
        st.plotly_chart(country_bar, width='stretch')

    # Original data
    if online:
        display_original_data_checkbox(data, st.session_state.source_display)
    else:
        display_original_data_checkbox(data, "MODIS")

# Show API request URL at bottom
if st.session_state.get("api_url"):
    st.divider()
    st.write("### API Request Used")
    st.code(st.session_state.api_url, language="text")
else:
    st.info("Enter a bounding box and click **Submit & Refresh** to load data")