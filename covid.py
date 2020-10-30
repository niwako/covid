from datetime import datetime, timezone

import humanize
import streamlit as st

import data


def flag_header(iso_3166, header):
    """Streamlit function to display some header text along with a country flag.

    Parameters
    ----------
    iso_3166 : str
        The ISO 3166 two letter country code for the desired flag.

    header : str
        The header text to display next to the flag.
    """
    flag_url = data.flag_url(iso_3166)
    st.markdown(
        f'<h2><img src="{flag_url}" height="32" /> {header}</h2>',
        unsafe_allow_html=True,
    )


"""
# Covid Data
"""

now = datetime.now(timezone.utc)
ldf = data.latest_covid_by_country()

confirmed = ldf.confirmed.sum()
recovered = ldf.recovered.sum()
deaths = ldf.deaths.sum()

f"""
Last updated {humanize.naturaltime(data.last_update(), when=now)}.

## Worldwide

| Total cases   | Recovered     | Deaths     |
| ---           | ---           | ---        |
| {confirmed:,} | {recovered:,} | {deaths:,} |
"""

# Get the latest country level data for the United States.
row = ldf[ldf.country_region == "United States"].iloc[0]
flag_header(row.iso_3166, row.country_region)

f"""
| Total cases       | Recovered         | Deaths         |
| ---               | ---               | ---            |
| {row.confirmed:,} | {row.recovered:,} | {row.deaths:,} |
"""
