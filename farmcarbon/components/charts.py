"""Reusable Plotly charts."""
import pandas as pd
import plotly.express as px
import streamlit as st


def render_index_chart(records, index="ndvi", title=None):
    if not records:
        st.info("No observations available yet.")
        return
    df = pd.DataFrame(records)
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    fig = px.line(df, x="observation_date", y=index, color="farm_id", markers=True,
                  title=title or f"{index.upper()} time series")
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=50, b=10), legend_title="Farm")
    st.plotly_chart(fig, use_container_width=True)
