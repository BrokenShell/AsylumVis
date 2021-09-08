import os

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


def get_cases_df(case_type: str) -> pd.DataFrame:
    app_lookup = {
        "Initial Hearings": "SELECT * FROM cases WHERE application_type = 'initial'",
        "Appellate Hearings": "SELECT * FROM cases WHERE application_type = 'appellate'",
        "All Hearings": "SELECT * FROM cases",
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


def get_table(columns=None):
    if columns:
        return db_query(f"""SELECT {', '.join(col for col in columns)} 
        FROM cases;""")
    else:
        return db_query(f"SELECT * FROM cases;")


def delete_by_id(_id: str):
    db_action(f"DELETE FROM cases WHERE id = {_id}")


if __name__ == '__main__':
    print(get_table())
