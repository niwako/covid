#!/usr/bin/env python3
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

import etl


def cache(*args, **kwargs):
    def decorator(func):
        try:
            __IPYTHON__  # type: ignore
            return func
        except NameError:
            return st.cache(func, *args, **kwargs)

    return decorator


def flag_url(country_code):
    return f"https://raw.githubusercontent.com/hjnilsson/country-flags/master/svg/{country_code.lower()}.svg"


@cache(ttl=3600)
def last_update():
    with etl.sqlite() as con:
        dt = next(con.execute("SELECT max(last_update) FROM covid"))[0]
        return datetime.fromisoformat(dt).replace(tzinfo=timezone.utc)


@cache(ttl=3600)
def latest_covid_by_country():
    with etl.sqlite() as con:
        return pd.read_sql(
            """
            WITH
                max_date AS (
                    SELECT max(file_date) AS file_date
                    FROM covid
                ),
                covid_by_country AS (
                    SELECT
                        country_region,
                        file_date,
                        sum(confirmed) AS confirmed,
                        sum(deaths) AS deaths,
                        sum(recovered) AS recovered,
                        sum(active) AS active
                    FROM covid
                    JOIN max_date USING (file_date)
                    GROUP BY country_region, file_date
                )
            SELECT *
            FROM covid_by_country
            JOIN population USING (country_region)
            JOIN flags USING (country_region)
            """,
            con,
            parse_dates=["file_date"],
        )
