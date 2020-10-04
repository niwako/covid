#!/usr/bin/env python3
import os

import pandas as pd
import streamlit as st

import fetch

INTEGER_COLUMNS = ["confirmed", "deaths", "recovered", "active"]

COVID_COLUMN_REMAP = {
    "Province/State": "Province_State",
    "Country/Region": "Country_Region",
    "Last Update": "Last_Update",
    "Lat": "Latitude",
    "Long_": "Longitude",
    "Case-Fatality_Ratio": "Case_Fatality_Ratio",
}


def read_covid_csv(csv_file):
    df = pd.read_csv(csv_file)
    df = df.rename(COVID_COLUMN_REMAP, axis=1)
    df["Last_Update"] = pd.to_datetime(df.Last_Update)
    df["File_Date"] = pd.to_datetime(os.path.split(csv_file)[-1].split(".")[0])
    return df


@st.cache(ttl=3600)
def covid():
    fetch.covid_update()
    dfs = [read_covid_csv(csv_file) for csv_file in fetch.covid_csv_files()]

    df = pd.concat(dfs)
    df = df.sort_values(["File_Date", "Country_Region", "Province_State"])
    df = df.reset_index(drop=True)

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
    df = pd.read_csv(fetch.population_csv_file(), skiprows=2, header=1)
    df = df[df.columns[:-1]]
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
