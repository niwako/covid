import humanize
import pandas as pd
import streamlit as st

import data


cdf = data.covid()
pdf = data.population()
wdf = data.covid_by_country()

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
