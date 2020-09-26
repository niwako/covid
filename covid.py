import streamlit as st
import numpy as np
import pandas as pd
import data


@st.cache(ttl=3600)
def covid():
    return data.covid()


@st.cache
def population():
    return data.population()


"""
# Covid Data
"""

df = covid()

world_wide_deaths = int(
    df[(df.Last_Update == "2020-09-23 04:23:40")]
    .sort_values("Last_Update", ascending=False)
    .Deaths.sum()
)
st.write(f"Worldwide deaths: {world_wide_deaths:,}")
st.markdown(
    f"""
|Deaths|
|---|
|{world_wide_deaths:,}|
"""
)
