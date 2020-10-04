import humanize
import pandas as pd
import streamlit as st

import data


def flag_header(iso_3361, header):
    flag_url = data.flag_url(iso_3361)
    st.markdown(
        f'<h2><img src="{flag_url}" height="32" /> {header}</h2>',
        unsafe_allow_html=True,
    )


cdf = data.covid()
wdf = data.covid_by_country()

"""
# Covid Data
"""

ldf = wdf[(wdf.file_date == max(wdf.file_date))]

confirmed = ldf.confirmed.sum()
recovered = ldf.recovered.sum()
deaths = ldf.deaths.sum()

f"""
Last updated {humanize.naturaltime(max(cdf.last_update))}.

## Worldwide

| Total cases   | Recovered     | Deaths     |
| ---           | ---           | ---        |
| {confirmed:,} | {recovered:,} | {deaths:,} |
"""

COUNTRY = "United States"
row = ldf[ldf.country_region == COUNTRY].iloc[0]
flag_header(row.iso_3361, row.country_region)

f"""
| Total cases       | Recovered         | Deaths         |
| ---               | ---               | ---            |
| {row.confirmed:,} | {row.recovered:,} | {row.deaths:,} |
"""
