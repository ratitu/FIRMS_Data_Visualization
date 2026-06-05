"""Visualization module for FIRMS Data Visualization."""

import pandas as pd
import plotly.express as px
from typing import Optional
import streamlit as st

from config import BADGE_COLORS


def create_badge(label: str, value: str, color: str) -> str:
    """Create a shields.io badge markdown."""
    safe_value = value.replace(" ", "%20").replace(",", "%2C")
    return f"![](https://img.shields.io/badge/{label}-{safe_value}-{color})"


def create_badges(badge_data: list[tuple[str, str, str]]) -> str:
    """Create multiple badges joined by spaces."""
    return " ".join(create_badge(label, value, color) for label, value, color in badge_data)


@st.cache_data
def create_date_line_chart(data: pd.DataFrame) -> Optional[object]:
    """Create a line chart showing fire counts by date."""
    if "acq_date" not in data.columns or data.empty:
        return None

    date_count = data.groupby("acq_date").size().reset_index(name="count")

    if date_count["acq_date"].nunique() <= 1:
        return None

    fig = px.line(date_count, x="acq_date", y="count")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        template="plotly_white",
    )
    return fig


@st.cache_data
def create_country_bar_chart(
    data: pd.DataFrame, countries_dict: dict[str, str]
) -> Optional[object]:
    """Create a bar chart showing fire counts by country."""
    if "country_id" not in data.columns or data.empty:
        return None

    country_count = data.groupby("country_id").size().reset_index(name="count")
    country_count["country"] = country_count["country_id"].map(countries_dict)

    if country_count["country"].nunique() <= 1:
        return None

    fig = px.bar(country_count, x="country", y="count")
    fig.update_layout(
        xaxis_title="Country",
        yaxis_title="Count",
        template="plotly_white",
    )
    return fig


@st.cache_data
def create_date_by_country_line_chart(data: pd.DataFrame) -> Optional[object]:
    """Create a line chart showing fire counts by date, separated by country."""
    required_cols = {"acq_date", "country"}
    if not required_cols.issubset(data.columns) or data.empty:
        return None

    date_country_count = (
        data.groupby(["acq_date", "country"]).size().reset_index(name="count")
    )

    fig = px.line(date_country_count, x="acq_date", y="count", color="country")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Count",
        template="plotly_white",
    )
    return fig


FIRE_HOVER_COLS = [
    "acq_date", "brightness", "bright_t31", "frp", "confidence",
    "satellite", "daynight",
]


def create_fire_map(data: pd.DataFrame) -> Optional[object]:
    """Create a scatter map with fire data points and hover tooltips."""
    if data.empty or "latitude" not in data.columns or "longitude" not in data.columns:
        return None

    hover_cols = [c for c in FIRE_HOVER_COLS if c in data.columns]

    fig = px.scatter_map(
        data,
        lat="latitude",
        lon="longitude",
        hover_name=None,
        hover_data={c: True for c in hover_cols},
        color_discrete_sequence=["red"],
        size_max=8,
        zoom=2,
        map_style="open-street-map",
    )

    fig.update_traces(
        marker={"size": 5, "opacity": 0.7},
        selector=dict(type="scattermap"),
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=600,
    )

    return fig


def display_online_badges(
    country_display: str, date_display: str, date_range_display: str
) -> None:
    """Display badges for online mode."""
    badges = [
        ("Country", country_display, BADGE_COLORS["country"]),
        ("Date", date_display, BADGE_COLORS["date"]),
        ("Date Range", date_range_display, BADGE_COLORS["date_range"]),
    ]
    st.write(create_badges(badges))


def display_local_badges(year_begin: int, year_end: int, countries: list[str]) -> None:
    """Display badges for local mode."""
    country_badges = [c.replace(" ", "%20") for c in countries]
    badges = [
        ("Years", f"{year_begin}--{year_end}", BADGE_COLORS["years"]),
        ("Countries", ",%20".join(country_badges), BADGE_COLORS["country"]),
    ]
    st.write(create_badges(badges))


def display_source_badge(source_display: str) -> None:
    """Display source/instrument badge."""
    st.write(
        create_badge("Instrument", source_display, BADGE_COLORS["instrument"])
    )


def render_clicked_point(data: pd.DataFrame) -> None:
    """Display details of the clicked fire point from selection."""
    if data.empty:
        return

    selected = st.session_state.get("fire_map")
    if not selected:
        return

    points = selected.get("selection", {}).get("points", [])
    if not points:
        return

    point = points[0]
    lat = point.get("lat")
    lon = point.get("lon")

    if lat is None or lon is None:
        return

    match = data[(data["latitude"] == lat) & (data["longitude"] == lon)]
    if not match.empty:
        st.write("#### Fire Point Details")
        st.write(match.iloc[0].to_frame().to_markdown())