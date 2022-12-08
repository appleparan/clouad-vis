import asyncio
from pathlib import Path

import aiohttp
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import tomli as toml
from plotly.subplots import make_subplots
from sklearn.datasets import load_iris


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            result = await response.json()
            return result
    except Exception:
        return {}


async def main(config: dict[str, str] = None):
    if config is None:
        data = load_iris(as_frame=True).data
        datasets = ["iris"]
        base_uri = "http://localhost:8000"
        col1 = {
            "x": data.index,
            "y": data["sepal length (cm)"],
            "name": "sepal length (cm)",
            "mode": "lines",
            "marker_color": "#fb3838",
            "line_color": "#fb3838",
        }
        col2 = {
            "x": data.index,
            "y": data["sepal width (cm)"],
            "name": "sepal width (cm)",
            "mode": "lines",
            "marker_color": "#999797",
            "line_color": "#999797",
        }
        data["anomaly"] = 0
        data.loc[data["petal length (cm)"] > 6, "anomaly"] = 1

        col3 = {
            "x": data[data["anomaly"] == 1].index,
            "y": data[data["anomaly"] == 1]["sepal length (cm)"],
            "name": "Anomaly",
            "mode": "markers",
            "marker_color": "#9e2121",
            "marker_symbol": "x",
            "marker_size": 10,
            "line_color": "#9e2121",
        }
    else:
        data = None
        datasets = config["datasets"]
        base_uri = config["base_uri"]
        col1 = config["col1"]
        col2 = config["col2"]

    st.set_page_config(page_title="Monitoring", page_icon="📈")
    st.title("Anomaly monitor")

    async with aiohttp.ClientSession() as session:
        with st.form("my_form"):
            selection = st.selectbox("Select dataset", datasets)

            fetched = st.form_submit_button("Fetch")

            if fetched:
                if data is None:
                    data = await fetch(session, f"{base_uri}/data/{selection}")

                if data is not None:
                    st.plotly_chart(get_figure(data, col_re=col1, col_rt=col2, col_am=col3))
                else:
                    st.error("Error")


def get_figure(
    data: pd.DataFrame,
    col_re: dict[str, str],
    col_rt: dict[str, str],
    col_am: dict[str, str] = None,
):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces for reconstruction error
    fig.add_trace(
        go.Scatter(
            x=col_re["x"],
            y=col_re["y"],
            name=col_re["name"],
            mode=col_re["mode"],
            marker_color=col_re["marker_color"],
            line_color=col_re["line_color"],
        ),
        secondary_y=False,
    )

    # Add traces for reconstruction error
    if col_am is not None:
        fig.add_trace(
            go.Scatter(
                x=col_am["x"],
                y=col_am["y"],
                name=col_am["name"],
                mode=col_am["mode"],
                marker_color=col_am["marker_color"],
                marker_size=col_am["marker_size"],
                marker_symbol=col_am["marker_symbol"],
                line_color=col_am["line_color"],
            ),
            secondary_y=False,
        )

    # Add traces for reconstruction error
    fig.add_trace(
        go.Scatter(
            x=col_rt["x"],
            y=col_rt["y"],
            name=col_rt["name"],
            mode=col_rt["mode"],
            marker_color=col_rt["marker_color"],
            line_color=col_rt["line_color"],
        ),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(title_text="Reconstruction error & Response Time")

    return fig


if __name__ == "__main__":
    toml_path = Path("config.toml")
    cfg = None
    if toml_path.exists():
        with open(toml_path) as f:
            cfg = toml.load(f)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(config=cfg))
