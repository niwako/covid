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
COVID_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
COVID_DAILY_REPORTS_DIR = "csse_covid_19_data/csse_covid_19_daily_reports"

COVID_SQLITE = os.path.join(DATA_DIR, "covid.sqlite")

os.makedirs(DATA_DIR, exist_ok=True)


def covid_update():
    if os.path.exists(os.path.join(DATA_DIR, COVID_DIR)):
        subprocess.call(
            ["git", "pull", "--rebase", "origin", "master"],
            cwd=os.path.join(DATA_DIR, COVID_DIR),
        )
    else:
        subprocess.call(["git", "clone", COVID_REPO, COVID_DIR], cwd=DATA_DIR)


def covid_csv_files():
    return glob.glob(
        os.path.join(DATA_DIR, COVID_DIR, COVID_DAILY_REPORTS_DIR, "*.csv")
    )


def read_covid_csv(csv_file):
    df = pd.read_csv(csv_file)
    df = df.rename(
        {
            "Province/State": "Province_State",
            "Country/Region": "Country_Region",
            "Last Update": "Last_Update",
            "Lat": "Latitude",
            "Long_": "Longitude",
            "Case-Fatality_Ratio": "Case_Fatality_Ratio",
        },
        axis=1,
    )

    df.columns = [s.lower() for s in df.columns]
    df["last_update"] = pd.to_datetime(df.last_update)
    df["file_date"] = pd.to_datetime(os.path.split(csv_file)[-1].split(".")[0])

    prev_len = len(df)
    pk = ["file_date", "country_region", "province_state"]
    if "admin2" in df:
        pk.append("admin2")
    df = df.drop_duplicates(subset=pk)
    new_len = len(df)
    if new_len != prev_len:
        print(f"Warning: Dropped {prev_len - new_len} rows while processing {csv_file}")

    for int_col in ["confirmed", "deaths", "recovered", "active"]:
        if int_col in df:
            df[int_col] = df[int_col].fillna(0).astype("int")
        else:
            df[int_col] = 0

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


def covid():
    covid_update()

    with sqlite() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS covid (
                file_date TIMESTAMP NOT NULL,
                country_region TEXT NOT NULL,
                province_state TEXT,
                admin2 TEXT,
                last_update TIMESTAMP NOT NULL,
                confirmed INTEGER NOT NULL,
                deaths INTEGER NOT NULL,
                recovered INTEGER NOT NULL,
                active INTEGER NOT NULL,
                fips INTEGER,
                latitude REAL,
                longitude REAL,
                combined_key TEXT,
                incidence_rate REAL,
                case_fatality_ratio REAL,
                PRIMARY KEY (file_date, country_region, province_state, admin2)
            )"""
        )

        loaded = set(
            pd.read_sql(
                "SELECT DISTINCT file_date FROM covid", con, parse_dates=["file_date"]
            ).file_date
        )
        for csv_file in covid_csv_files():
            file_date = datetime.datetime.strptime(
                os.path.split(csv_file)[-1].split(".")[0], r"%m-%d-%Y"
            )
            if file_date not in loaded:
                print(f"Loading {csv_file}")
                df = read_covid_csv(csv_file)
                df.to_sql("covid", con, if_exists="append", index=False)


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

    with sqlite() as con:
        con.execute("DROP TABLE IF EXISTS population")
        con.execute(
            """
            CREATE TABLE population (
                country_region TEXT NOT NULL,
                population INTEGER,
                PRIMARY KEY (country_region)
            )
            """
        )
        df.to_sql("population", con, if_exists="append", index=False)


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

    with sqlite() as con:
        con.execute("DROP TABLE IF EXISTS flags")
        con.execute(
            """
            CREATE TABLE flags (
                country_region TEXT NOT NULL,
                iso_3166 TEXT,
                PRIMARY KEY (country_region)
            )
            """
        )
        df.to_sql("flags", con, if_exists="append", index=False)


@contextlib.contextmanager
def sqlite():
    with sqlite3.connect(COVID_SQLITE) as con:
        yield con


def etl():
    population()
    flags()
    covid()


if __name__ == "__main__":
    etl()
