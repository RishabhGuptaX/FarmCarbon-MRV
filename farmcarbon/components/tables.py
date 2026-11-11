"""Dataframe helpers."""
import pandas as pd
import streamlit as st

def show_records(records, columns=None):
    if not records:
        st.info("No records to show yet.")
        return
    df = pd.DataFrame(records)
    if columns:
        keep = [c for c in columns if c in df.columns]
        df = df[keep]
    st.dataframe(df, use_container_width=True, hide_index=True)
