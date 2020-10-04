#!/usr/bin/env python3
import datetime
import glob
import os
import subprocess

DATA_DIR = "data"

POP_DIR = os.path.join(DATA_DIR, "population")
POP_ZIP = "population.zip"
POP_URL = "http://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"

COVID_DIR = "covid"
COVID_STATE_FILE = "covid.state"
COVID_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
COVID_DAILY_REPORTS_DIR = "csse_covid_19_data/csse_covid_19_daily_reports"

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


if __name__ == "__main__":
    covid_update(force=True)
