import awswrangler as wr
import streamlit as st
import pandas as pd
import numpy as np

DT_COL = "DepartureDateTime"
wr.config.s3_endpoint_url = "http://127.0.0.1:4566"


def _unpack_payload(d: pd.DataFrame) -> pd.DataFrame:
    """Unpack (normalize) the json payload of messages"""
    json_data = pd.json_normalize(d["data"])

    ret = d.drop("data", axis=1)
    return pd.concat([ret, json_data], axis=1)


def load_data():
    # pip install "pandas[aws,pyarrow,fastparquet]"
    # pip install awswrangler

    # Read from S3
    # storage_options = {"client_kwargs": {"endpoint_url": "http://127.0.0.1:4566"}}
    # s3path = "s3://my-bucket/topics/foo/year=2024/month=04/day=15/hour=12/foo+0+0000000002.snappy.parquet"
    #    df = pd.read_parquet(, storage_options=storage_options)
    s3path = "s3://my-bucket/topics/foo/"
    df = wr.s3.read_parquet(path=s3path, dataset=True)
    # partition_filter=lambda x: x["year"] == "2020"
    df = _unpack_payload(df)
    df = cast_datetime_col(df)
    return df

def cast_datetime_col(data):
    data[DT_COL] = pd.to_datetime(data[DT_COL])
    return data

def histogram(data: pd.DataFrame) -> None:
    """Prediction by hour (Could be interesting for SLA (e.g. predictions come in late)"""
    st.subheader("Prediction date-time by hour.")
    hist_values = np.histogram(
        data[DT_COL].dt.hour, bins=24, range=(0, 24)
    )[0]
    st.bar_chart(hist_values)


def show_dataframe(data: pd.DataFrame) -> None:
    st.subheader("data as dafaframe")
    st.dataframe(data)

def show_chart(data: pd.DataFrame, chart) -> None:
    color_map = {2:"#8aff80", 3:"#ff80bf", 94: "#ffcc80"}
    st.subheader("Plot")
    data["ModelMetaDataversion"] = data["ModelMetaData.version"].map(color_map)
    chart(
        data,
        x=DT_COL,
        y="PredictedFreightLanemeters",
        color="ModelMetaDataversion",
        width=300,
    )

def get_dash():
    st.title("RoPax - Monitoring")
    data_load_state = st.text("Loading data...")
    data = load_data()
    data_load_state.text("Loading data...done!")
    st.subheader("Raw data")
    st.write(data.head())
    histogram(data)
    show_chart(data, st.scatter_chart)
    show_chart(data, st.line_chart)

if __name__ == "__main__":
    get_dash()
