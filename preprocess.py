#!/usr/bin/env python3
import os

import pandas as pd

import data

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


def covid():
    data.update_covid_repo()
    dfs = [read_covid_csv(csv_file) for csv_file in data.covid_csv_files()]

    df = pd.concat(dfs)
    df = df.sort_values(["File_Date", "Country_Region", "Province_State"])
    df = df.reset_index(drop=True)
    return df


def population():
    df = pd.read_csv(data.population_csv_files()[0], skiprows=2, header=1)
    return df[df.columns[:-1]]
