import os

import pandas as pd
import requests
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


def cache(*args, **kwargs):
    def decorator(func):
        try:
            __IPYTHON__  # type: ignore
            return func
        except NameError:
            return st.cache(func, *args, **kwargs)

    return decorator


def read_covid_csv(csv_file):
    df = pd.read_csv(csv_file)
    df = df.rename(COVID_COLUMN_REMAP, axis=1)
    df["Last_Update"] = pd.to_datetime(df.Last_Update)
    df["File_Date"] = pd.to_datetime(os.path.split(csv_file)[-1].split(".")[0])
    return df


@cache(ttl=3600)
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
            "Ivory Coast": "Cote d'Ivoire",
            "Korea, South": "South Korea",
            "Macao SAR": "Macau",
            "Mainland China": "China",
            "North Ireland": "Ireland",
            "Republic of Ireland": "Ireland",
            "Republic of Korea": "South Korea",
            "Republic of Moldova": "Moldova",
            "Republic of the Congo": "Congo (Brazzaville)",
            "Russian Federation": "Russia",
            "St. Martin": "Saint Martin",
            "Taiwan*": "Taiwan",
            "The Bahamas": "Bahamas",
            "The Gambia": "Gambia",
            "UK": "United Kingdom",
            "US": "United States",
            "Viet Nam": "Vietnam",
        }
    )
    return df


@cache()
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
            "St. Martin (French part)": "Saint Martin",
            "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
            "Slovak Republic": "Slovakia",
            "Syrian Arab Republic": "Syria",
            "Venezuela, RB": "Venezuela",
            "Viet Nam": "Vietnam",
            "Yemen, Rep.": "Yemen",
        }
    )
    return df


@cache()
def flags():
    resp = requests.get(
        "https://raw.githubusercontent.com/hjnilsson/country-flags/master/countries.json"
    )
    df = pd.DataFrame(resp.json().items(), columns=["iso_3166", "country_region"])
    df = df[["country_region", "iso_3166"]]
    df["country_region"] = df["country_region"].replace(
        {
            "Bolivia, Plurinational State of": "Bolivia",
            "Brunei Darussalam": "Brunei",
            "Cape Verde": "Cabo Verde",
            "Congo": "Congo (Brazzaville)",
            "Congo, the Democratic Republic of the": "Congo (Kinshasa)",
            "Côte d'Ivoire": "Cote d'Ivoire",
            "Curaçao": "Curacao",
            "Holy See (Vatican City State)": "Holy See",
            "Iran, Islamic Republic of": "Iran",
            "Korea, Republic of": "South Korea",
            "Lao People's Democratic Republic": "Laos",
            "Macao": "Macau",
            "Macedonia, the former Yugoslav Republic of": "North Macedonia",
            "Moldova, Republic of": "Moldova",
            "Russian Federation": "Russia",
            "Saint Barthélemy": "Saint Barthelemy",
            "Syrian Arab Republic": "Syria",
            "Swaziland": "Eswatini",
            "Tanzania, United Republic of": "Tanzania",
            "Venezuela, Bolivarian Republic of": "Venezuela",
        }
    )
    return df


def flag_url(country_code):
    return f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/{country_code.lower()}.svg"


@cache(ttl=3600)
def covid_by_country():
    covid_df = covid()
    pop_df = population()
    flags_df = flags()
    df = covid_df.groupby(["country_region", "file_date"])[INTEGER_COLUMNS].sum()
    df = df.reset_index()
    df = pd.merge(df, pop_df, on="country_region")
    df = pd.merge(df, flags_df, on="country_region")
    return df
