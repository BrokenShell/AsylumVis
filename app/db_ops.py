import os
from typing import Union

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()
db_url = os.getenv('DB_URL')


def db_action(sql_action: str):
    """ DB Setter - Performs a DB action returns None """
    conn = psycopg2.connect(db_url)
    curs = conn.cursor()
    curs.execute(sql_action)
    conn.commit()
    curs.close()
    conn.close()


def db_query(sql_query) -> list:
    """ DB Getter - Returns query results as a list """
    conn = psycopg2.connect(db_url)
    curs = conn.cursor()
    curs.execute(sql_query)
    results = curs.fetchall()
    curs.close()
    conn.close()
    return results


def outcome_counts(judge_id: int):
    return {k: v for k, v in db_query(f"""SELECT outcome, COUNT( outcome ) 
    FROM cases WHERE judge_id = {judge_id}
    GROUP BY outcome;""")}


def get_cases_df(case_type: str) -> pd.DataFrame:
    app_lookup = {
        "Appellate": "SELECT * FROM cases WHERE appellate = true",
        "Initial": "SELECT * FROM cases WHERE appellate = false",
        "All Cases": "SELECT * FROM cases",
    }
    conn = psycopg2.connect(db_url)
    curs = conn.cursor()
    curs.execute(app_lookup[case_type])
    cols = [k[0] for k in curs.description]
    rows = curs.fetchall()
    df = pd.DataFrame(rows, columns=cols)
    curs.close()
    conn.close()
    return df
