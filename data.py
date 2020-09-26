#!/usr/bin/env python3
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


def covid():
    if os.path.exists(os.path.join(DATA_DIR, COVID_DIR)):
        print(f"Pulling CSSEGISandData/COVID-19.git")
        subprocess.call(["git", "pull"], cwd=os.path.join(DATA_DIR, COVID_DIR))
    else:
        print(f"Cloning CSSEGISandData/COVID-19.git to {DATA_DIR}")
        subprocess.call(["git", "clone", COVID_REPO, COVID_DIR], cwd=DATA_DIR)

    csv_files = glob.glob(
        os.path.join(DATA_DIR, COVID_DIR, COVID_DAILY_REPORTS_DIR, "*.csv")
    )
    dfs = [
        pd.read_csv(csv_file).rename(COVID_COLUMN_REMAP, axis=1)
        for csv_file in csv_files
    ]
    return pd.concat(dfs)


def population():
    subprocess.call(["rm", "-rf", POP_DIR])
    os.makedirs(POP_DIR, exist_ok=True)
    subprocess.call(["curl", POP_URL, "-o", POP_ZIP], cwd=POP_DIR)
    subprocess.call(["unzip", "-u", POP_ZIP], cwd=POP_DIR)

    csv_file = glob.glob(os.path.join(POP_DIR, "API_SP.POP.TOTL*.csv"))[0]
    return pd.read_csv(csv_file, skiprows=2, header=1)
