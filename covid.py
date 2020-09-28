import streamlit as st
import numpy as np
import pandas as pd
import data


INTEGER_COLUMNS = ("confirmed", "deaths", "recovered", "active")


@st.cache(ttl=3600)
def covid():
    df = data.covid()
    df.columns = [s.lower() for s in df.columns]
    for int_col in INTEGER_COLUMNS:
        df[int_col] = df[int_col].fillna(0).astype("int")
    df["country_region"] = df["country_region"].replace(
        {
            "Bahamas, The": "Bahamas",
            "Burma": "Myanmar",
            "Czech Republic": "Czechia",
            "Gambia, The": "Gambia",
            "Hong Kong SAR": "Hong Kong",
            "Iran (Islamic Republic of)": "Iran",
            "Korea, South": "South Korea",
            "Macao SAR": "Macau",
            "Mainland China": "China",
            "North Ireland": "Ireland",
            "Republic of Ireland": "Ireland",
            "Republic of Korea": "South Korea",
            "Republic of Moldova": "Moldova",
            "Republic of the Congo": "Congo (Brazzaville)",
            "Russian Federation": "Russia",
            "The Bahamas": "Bahamas",
            "The Gambia": "Gambia",
            "UK": "United Kingdom",
            "Viet Nam": "Vietnam",
        }
    )
    return df


@st.cache
def population():
    df = data.population()
    df = df.rename({"Country Name": "country_region", "2019": "population"}, axis=1)
    df = df[["country_region", "population"]]
    df["country_region"] = df["country_region"].replace(
        {
            "Bahamas, The": "Bahamas",
            "Brunei Darussalam": "Brunei",
            "Congo, Rep.": "Congo (Brazzaville)",
            "Congo, Dem. Rep.": "Congo (Kinshasa)",
            "Czech Republic": "Czechia",
            "Egypt, Arab Rep.": "Egypt",
            "Gambia, The": "Gambia",
            "Hong Kong SAR, China": "Hong Kong",
            "Iran, Islamic Rep.": "Iran",
            "Korea, Rep.": "South Korea",
            "Kyrgyz Republic": "Kyrgyzstan",
            "Lao PDR": "Laos",
            "Macao SAR, China": "Macau",
            "Russian Federation": "Russia",
            "St. Kitts and Nevis": "Saint Kitts and Nevis",
            "St. Lucia": "Saint Lucia",
            "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
            "Slovak Republic": "Slovakia",
            "Syrian Arab Republic": "Syria",
            "United States": "US",
            "Venezuela, RB": "Venezuela",
            "Yemen, Rep.": "Yemen",
        }
    )
    return df


def covid_by_country(cdf, pdf):
    wdf = cdf.groupby(["country_region", "file_date"])[INTEGER_COLUMNS].sum()
    wdf = wdf.reset_index()
    wdf = pd.merge(wdf, pdf, on="country_region")
    return wdf


cdf = covid()
pdf = population()
wdf = covid_by_country(cdf, pdf)

"""
# Covid Data
"""

wdf

latest = max(cdf.last_update)
ldf = cdf[(cdf.last_update == latest)]
ldf

confirmed = ldf.confirmed.sum()
recovered = ldf.recovered.sum()
deaths = ldf.deaths.sum()

f"""
{latest}

## Worldwide

| Total cases   | Recovered     | Deaths     |
| ---           | ---           | ---        |
| {confirmed:,} | {recovered:,} | {deaths:,} |
"""
