#!/usr/bin/env python3
import datetime
import glob
import os
import subprocess

import pandas as pd

DATA_DIR = "data"

POP_DIR = os.path.join(DATA_DIR, "population")
POP_ZIP = "population.zip"
POP_URL = "http://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"

COVID_DIR = "covid"
COVID_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
COVID_DAILY_REPORTS_DIR = "csse_covid_19_data/csse_covid_19_daily_reports"
COVID_COLUMN_REMAP = {
    "Province/State": "Province_State",
    "Country/Region": "Country_Region",
    "Last Update": "Last_Update",
    "Lat": "Latitude",
    "Long_": "Longitude",
    "Case-Fatality_Ratio": "Case_Fatality_Ratio",
}

os.makedirs(DATA_DIR, exist_ok=True)


def update_covid_repo():
    now = datetime.datetime.now()
    last_update_file = os.path.join(DATA_DIR, "covid.last_update")
    if os.path.exists(last_update_file):
        with open(last_update_file, "r") as fp:
            last_update = datetime.datetime.fromisoformat(fp.read())
        if now - last_update < datetime.timedelta(seconds=3600):
            return

    if os.path.exists(os.path.join(DATA_DIR, COVID_DIR)):
        subprocess.call(
            ["git", "pull", "--rebase", "origin", "master"],
            cwd=os.path.join(DATA_DIR, COVID_DIR),
        )
    else:
        subprocess.call(["git", "clone", COVID_REPO, COVID_DIR], cwd=DATA_DIR)

    with open(last_update_file, "w") as fp:
        fp.write(str(now))


def read_covid_csv(csv_file):
    df = pd.read_csv(csv_file)
    df = df.rename(COVID_COLUMN_REMAP, axis=1)
    df["Last_Update"] = pd.to_datetime(df.Last_Update)
    df["File_Date"] = pd.to_datetime(os.path.split(csv_file)[-1].split(".")[0])
    return df


def covid():
    update_covid_repo()
    csv_files = glob.glob(
        os.path.join(DATA_DIR, COVID_DIR, COVID_DAILY_REPORTS_DIR, "*.csv")
    )
    dfs = [read_covid_csv(csv_file) for csv_file in csv_files]

    df = pd.concat(dfs)
    df = df.sort_values(["File_Date", "Country_Region", "Province_State"])
    df = df.reset_index(drop=True)
    return df


def population_csv_files():
    return glob.glob(os.path.join(POP_DIR, "API_SP.POP.TOTL*.csv"))


def population():
    if len(population_csv_files()) == 0:
        os.makedirs(POP_DIR, exist_ok=True)
        subprocess.call(["curl", POP_URL, "-o", POP_ZIP], cwd=POP_DIR)
        subprocess.call(["unzip", "-u", POP_ZIP], cwd=POP_DIR)

    df = pd.read_csv(population_csv_files()[0], skiprows=2, header=1)
    return df[df.columns[:-1]]


if __name__ == "__main__":
    update_covid_repo()
