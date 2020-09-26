import streamlit as st
import numpy as np
import pandas as pd
import data


@st.cache(ttl=3600)
def covid():
    df = data.covid()
    for int_col in ("Confirmed", "Deaths", "Recovered", "Active"):
        df[int_col] = df[int_col].fillna(0).astype("int")
    return df


@st.cache
def population():
    return data.population()


"""
# Covid Data
"""

df = covid()

latest = max(df.Last_Update)
ldf = df[(df.Last_Update == latest)]
ldf

confirmed = ldf.Confirmed.sum()
recovered = ldf.Recovered.sum()
deaths = ldf.Deaths.sum()

f"""
{latest}

## Worldwide

| Total cases   | Recovered     | Deaths     |
| ---           | ---           | ---        |
| {confirmed:,} | {recovered:,} | {deaths:,} |
"""
