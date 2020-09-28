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


@st.cache(ttl=3600)
def merge():
    cdf = covid()
    for int_col in ("Confirmed", "Deaths", "Recovered", "Active"):
        cdf[int_col] = cdf[int_col].fillna(0).astype("int")
    cdf["Country_Region"] = cdf["Country_Region"].replace(
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

    pdf = population()
    pdf = pdf[["Country Name", "2019"]]
    pdf["Country Name"] = pdf["Country Name"].replace(
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
    pdf = pdf.rename({"Country Name": "Country_Region", "2019": "Population"}, axis=1)
    df = pd.merge(cdf, pdf, how="inner", on="Country_Region")
    return df


"""
# Covid Data
"""

df = merge()

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
