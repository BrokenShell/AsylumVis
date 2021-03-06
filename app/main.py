""" Asylum Visualizer for Human Rights First """
import itertools

import requests as requests
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.db_ops import get_cases_df, get_table

APP = Flask(__name__)


@APP.route("/")
def home():
    return render_template("home.html")


@APP.route("/bars/", methods=["GET", "POST"])
def bars():
    columns = [
        "outcome",
        "gender",
        "application_type",
        "country_of_origin",
        "case_origin_state",
        "protected_grounds",
        "type_of_violence",
    ]
    col_1 = request.values.get("col_1") or "gender"
    col_2 = request.values.get("col_2") or "outcome"
    case_type = request.values.get("case_type") or "Initial Hearings"
    bar_type = request.values.get("bar_type") or "Stacked"
    df = get_cases_df(case_type)
    df_cross = pd.crosstab(df[col_1], df[col_2])
    col_1_name = col_1.title().replace('_', ' ')
    col_2_name = col_2.title().replace('_', ' ')
    if col_1 == col_2:
        title = f"{col_1_name} Totals"
    else:
        title = f"{col_2_name} by {col_1_name}"
    bar_lookup = {
        "Stacked": "stack",
        "Grouped": "group",
    }
    data = [
        go.Bar(name=col, x=df_cross.index, y=df_cross[col])
        for col in df_cross.columns
    ]
    layout = go.Layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=px.colors.qualitative.Antique,
        height=600,
        width=820,
        barmode=bar_lookup[bar_type],
        yaxis={"tickformat": ",", "title": "People"},
        xaxis={'title': col_1_name}
    )
    figure = go.Figure(data, layout)
    return render_template(
        "bars.html",
        options=columns,
        graph_json=figure.to_json(),
        selector_1=col_1,
        selector_2=col_2,
        case_type=case_type,
        bar_type=bar_type,
    )


@APP.route("/lines/", methods=["GET", "POST"])
def lines():
    columns = [
        "outcome",
        "gender",
        "application_type",
        "country_of_origin",
        "case_origin_state",
        "protected_grounds",
        "type_of_violence",
    ]
    col = request.values.get("col") or "gender"
    case_type = request.values.get("case_type") or "Initial Hearings"
    line_width = request.values.get("line_width") or "Thin"
    df = get_cases_df(case_type)
    df['date'] = df['date'].apply(pd.to_datetime).apply(str)
    df_cross = pd.crosstab(df['date'], df[col])
    for column in df_cross.columns:
        df_cross[column] = list(itertools.accumulate(df_cross[column]))
    col_name = col.title().replace('_', ' ')
    title = f"{col_name} by Date"
    line_width_val = {
        "Medium": 2.5,
        "Thin": 1,
        "Thick": 6,
    }[line_width]
    data = [go.Scatter(
        x=df_cross.index, y=df_cross[col],
        name=col,
        line={"width": line_width_val}
    ) for col in df_cross.columns]
    layout = go.Layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=px.colors.qualitative.Antique,
        height=600,
        width=820,
        yaxis={"tickformat": ",", "title": "Cumulative Number of People"},
    )
    figure = go.Figure(data, layout)
    return render_template(
        "lines.html",
        options=columns,
        graph_json=figure.to_json(),
        selector=col,
        case_type=case_type,
        line_width=line_width,
    )


@APP.route("/pies/", methods=["GET", "POST"])
def pies():
    columns = [
        "outcome",
        "gender",
        "application_type",
        "country_of_origin",
        "case_origin_state",
        "protected_grounds",
        "type_of_violence",
    ]
    col = request.values.get("col") or "outcome"
    case_type = request.values.get("case_type") or "Initial Hearings"
    pie_type = request.values.get("pie_type") or "Ring"
    df = get_cases_df(case_type)[col].value_counts()
    labels = df.index
    values = df.values
    col_name = col.title().replace('_', ' ')
    title = f"Percentage of People by {col_name}"
    hole = {
        "Solid": 0.0,
        "Donut": 0.5,
        "Ring": 0.8,
    }[pie_type]
    data = go.Pie(labels=labels, values=values, hole=hole)
    layout = go.Layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=px.colors.qualitative.Antique,
        height=640,
        width=820,
    )
    figure = go.Figure(data, layout)
    figure.update_traces(
        textposition='outside',
        textfont_size=14,
        textinfo='percent+label',
    )
    return render_template(
        "pies.html",
        options=columns,
        graph_json=figure.to_json(),
        selector=col,
        case_type=case_type,
        pie_type=pie_type,
    )


@APP.route("/table/", methods=["GET", "POST"])
def table():
    uuid = request.values.get('uuid')
    if uuid:
        url = "http://hrf-asylum-ds-dev.us-east-1.elasticbeanstalk.com/pdf-ocr"
        requests.get(f"{url}/{uuid}")
    return render_template(
        "table.html",
        table=get_cases_df("All Hearings").to_html(index=False),
    )


if __name__ == '__main__':
    APP.run()
