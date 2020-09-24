#!/usr/bin/env python3
import glob
import os
import subprocess

import pandas as pd
from progress.bar import ShadyBar

DATA_DIR = "data"
COMPILED_DATA_CSV = "data.csv"
COVID_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
DAILY_REPORTS_DIR = "csse_covid_19_data/csse_covid_19_daily_reports"
COLUMN_REMAP = {
    "Province/State": "Province_State",
    "Country/Region": "Country_Region",
    "Last Update": "Last_Update",
    "Lat": "Latitude",
    "Long_": "Longitude",
    "Case-Fatality_Ratio": "Case_Fatality_Ratio",
}


def read_csv(csv_file, bar):
    bar.next()
    return pd.read_csv(csv_file).rename(COLUMN_REMAP, axis=1)


def main():
    if os.path.exists(DATA_DIR):
        print(f"Pulling CSSEGISandData/COVID-19.git")
        subprocess.call(["git", "pull"], cwd=DATA_DIR)
    else:
        print(f"Cloning CSSEGISandData/COVID-19.git to {DATA_DIR}")
        subprocess.call(["git", "clone", COVID_REPO, DATA_DIR])

    csv_files = glob.glob(os.path.join(DATA_DIR, DAILY_REPORTS_DIR, "*.csv"))

    with ShadyBar("Reading CSV files", max=len(csv_files)) as bar:
        dfs = [read_csv(csv_file, bar) for csv_file in csv_files]
    df = pd.concat(dfs)

    print(f"Saving {len(df):,} rows to {COMPILED_DATA_CSV}... ", end="", flush=True)
    df.to_csv(COMPILED_DATA_CSV, index=False)
    print(f"done!")


if __name__ == "__main__":
    main()
