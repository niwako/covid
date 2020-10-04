import humanize
import pandas as pd
import streamlit as st

import data


def covid_by_country(cdf, pdf):
    wdf = cdf.groupby(["country_region", "file_date"])[data.INTEGER_COLUMNS].sum()
    wdf = wdf.reset_index()
    wdf = pd.merge(wdf, pdf, on="country_region")
    return wdf


cdf = data.covid()
pdf = data.population()
wdf = covid_by_country(cdf, pdf)

st.dataframe(wdf.head())

"""
# Covid Data
"""

latest = max(cdf.last_update)
ldf = cdf[(cdf.last_update == latest)]

confirmed = ldf.confirmed.sum()
recovered = ldf.recovered.sum()
deaths = ldf.deaths.sum()

f"""
Last updated {humanize.naturaltime(latest)}.

## Worldwide

| Total cases   | Recovered     | Deaths     |
| ---           | ---           | ---        |
| {confirmed:,} | {recovered:,} | {deaths:,} |
"""
