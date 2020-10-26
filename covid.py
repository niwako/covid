import humanize
import pandas as pd
import streamlit as st

import data


@st.cache(ttl=3600)
def last_update():
    with data.sqlite() as con:
        return pd.read_sql("SELECT max(last_update) FROM covid", con)


@st.cache(ttl=3600)
def latest_covid_by_country():
    with data.sqlite() as con:
        return pd.read_sql(
            """
            WITH
                max_date AS (
                    SELECT max(file_date) AS file_date
                    FROM covid
                ),
                covid_by_country AS (
                    SELECT
                        country_region,
                        file_date,
                        sum(confirmed) AS confirmed,
                        sum(deaths) AS deaths,
                        sum(recovered) AS recovered,
                        sum(active) AS active
                    FROM covid
                    JOIN max_date USING (file_date)
                    GROUP BY country_region, file_date
                )
            SELECT *
            FROM covid_by_country
            JOIN population USING (country_region)
            JOIN flags USING (country_region)
            """,
            con,
        )


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

ldf = latest_covid_by_country()

confirmed = ldf.confirmed.sum()
recovered = ldf.recovered.sum()
deaths = ldf.deaths.sum()

f"""
Last updated {humanize.naturaltime(last_update())}.

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
