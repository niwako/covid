#!/usr/bin/env python3
import contextlib
import datetime
import glob
import os
import sqlite3
import subprocess

import pandas as pd
import requests

DATA_DIR = "data"

POP_DIR = os.path.join(DATA_DIR, "population")
POP_ZIP = "population.zip"
POP_URL = "http://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"

COVID_DIR = "covid"
COVID_STATE_FILE = "covid.state"
COVID_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
COVID_DAILY_REPORTS_DIR = "csse_covid_19_data/csse_covid_19_daily_reports"

COVID_SQLITE = os.path.join(DATA_DIR, "covid.sqlite")

INTEGER_COLUMNS = ["confirmed", "deaths", "recovered", "active"]

COVID_COLUMN_REMAP = {
    "Province/State": "Province_State",
    "Country/Region": "Country_Region",
    "Last Update": "Last_Update",
    "Lat": "Latitude",
    "Long_": "Longitude",
    "Case-Fatality_Ratio": "Case_Fatality_Ratio",
}


os.makedirs(DATA_DIR, exist_ok=True)


def covid_update(force=False, timeout=5400):
    now = datetime.datetime.now()
    state_file = os.path.join(DATA_DIR, COVID_STATE_FILE)

    if os.path.exists(os.path.join(DATA_DIR, COVID_DIR)):
        if not force and os.path.exists(state_file):
            with open(state_file, "r") as fp:
                last_update = datetime.datetime.fromisoformat(fp.read())
            if now - last_update < datetime.timedelta(seconds=timeout):
                return

        subprocess.call(
            ["git", "pull", "--rebase", "origin", "master"],
            cwd=os.path.join(DATA_DIR, COVID_DIR),
        )
    else:
        subprocess.call(["git", "clone", COVID_REPO, COVID_DIR], cwd=DATA_DIR)

    with open(state_file, "w") as fp:
        fp.write(str(now))


def covid_csv_files():
    return glob.glob(
        os.path.join(DATA_DIR, COVID_DIR, COVID_DAILY_REPORTS_DIR, "*.csv")
    )


def read_covid_csv(csv_file):
    df = pd.read_csv(csv_file)
    df = df.rename(COVID_COLUMN_REMAP, axis=1)
    df["Last_Update"] = pd.to_datetime(df.Last_Update)
    df["File_Date"] = pd.to_datetime(os.path.split(csv_file)[-1].split(".")[0])
    return df


def covid():
    covid_update()
    dfs = [read_covid_csv(csv_file) for csv_file in covid_csv_files()]

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


def population_csv_files():
    return glob.glob(os.path.join(POP_DIR, "API_SP.POP.TOTL*.csv"))


def population_update():
    os.makedirs(POP_DIR, exist_ok=True)
    subprocess.call(["curl", POP_URL, "-o", POP_ZIP], cwd=POP_DIR)
    subprocess.call(["unzip", "-u", POP_ZIP], cwd=POP_DIR)


def population_csv_file():
    if len(population_csv_files()) == 0:
        population_update()
    return population_csv_files()[0]


def population():
    df = pd.read_csv(population_csv_file(), skiprows=2, header=1)
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


@contextlib.contextmanager
def sqlite():
    if not os.path.exists(COVID_SQLITE):
        etl()
    with sqlite3.connect(COVID_SQLITE) as con:
        yield con


def etl():
    cdf = covid()
    pdf = population()
    fdf = flags()

    with sqlite() as con:
        cdf.to_sql("covid", con, if_exists="replace", index=False)
        pdf.to_sql("population", con, if_exists="replace", index=False)
        fdf.to_sql("flags", con, if_exists="replace", index=False)


if __name__ == "__main__":
    etl()
