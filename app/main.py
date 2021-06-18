import os

from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.db_ops import outcome_counts, get_cases_df

APP = Flask(__name__)
db_url = os.getenv("DB_URL")


@APP.route("/")
@APP.route("/home/")
def home():
    query = outcome_counts(2)
    labels = list(query.keys())
    values = list(query.values())
    data = [go.Pie(
        labels=labels,
        values=values,
        textinfo="label+percent",
        showlegend=False,
    )]
    layout = go.Layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=px.colors.qualitative.Antique,
        height=600,
        width=750,
    )
    fig = go.Figure(data=data, layout=layout)
    return render_template(
        "home.html",
        graph_json=fig.to_json(),
    )


@APP.route("/")
@APP.route("/graphs/", methods=["GET", "POST"])
def graphs():
    df = get_cases_df(is_appellate=False)
    columns = ['gender', 'outcome', 'judge_id', 'filed_in_one_year']
    if request.values:
        col_1, col_2, is_stack, *_ = request.values.values()
        # bars = ["stack", "group", "overlay", "relative"]
        df_cross = pd.crosstab(df[col_1], df[col_2])
        title = f"{col_2.title().replace('_', ' ')} by {col_1.title().replace('_', ' ')}"
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
            width=750,
            barmode="stack" if is_stack else "group",
            yaxis={"tickformat": ",d"},
        )
        figure = go.Figure(data, layout)
        return render_template(
            "graphs.html",
            options=columns,
            graph_json=figure.to_json(),
            selector_1=col_1,
            selector_2=col_2,
            checked="checked" if is_stack else "",
        )
    else:
        return render_template(
            "graphs.html",
            options=columns,
            selector_1="gender",
            selector_2="outcome",
            checked="checked",
        )


if __name__ == '__main__':
    APP.run()