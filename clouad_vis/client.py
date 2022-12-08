import asyncio
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import tomli as toml
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from plotly.subplots import make_subplots
from sklearn.datasets import load_iris


async def main(config: dict[str, str] = None):
    if config is None:
        data = load_iris(as_frame=True).data
        datasets = ["iris"]
        url = "http://localhost:8086"
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

        url = "http://localhost:8086"
        token = "my-token"
        org = "my-org"
        bucket = "my-bucket"
    else:
        data = None
        datasets = config["datasets"]

        col1 = config["col1"]
        col2 = config["col2"]
        col3 = config["col3"]

        url = config["url"]
        token = config["token"]
        org = config["org"]
        bucket = config["bucket"]

    st.set_page_config(page_title="Monitoring", page_icon="📈")
    st.title("Anomaly monitor")

    async with InfluxDBClientAsync(url=url, token=token, org=org, enable_gzip=True) as client:
        with st.form("my_form"):
            selection = st.selectbox("Select dataset", datasets)

            fetched = st.form_submit_button("Fetch")

            if fetched:
                # Stream of FluxRecords
                query_api = client.query_api()
                data = await query_api.query_data_frame(
                    f"from(bucket: {bucket}) "
                    "|> range(start: -7d) "
                    f'|> filter(fn: (r) => r["table"] == "{selection}")'
                )
                st.plotly_chart(get_figure(data, col_re=col1, col_rt=col2, col_am=col3))


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
