import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from collections import Counter
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import io
from templates.single_article import create_word_cloud_image
import plotly.graph_objs as go

def create_agg_dashboard_component(articles):
    all_articles = " ".join([article['content'] for article in articles])
    word_count_df = run_multi_article_analysis(all_articles)
    word_cloud_image = create_word_cloud_image(all_articles)
    layout = html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            dcc.Dropdown(
                                id="publication-dropdown",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "75%",
                                }),
                            dcc.Dropdown(
                                id="author-dropdown",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "75%",
                                }),
                            dcc.Dropdown(
                                id="month-dropdown",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "75%",
                                }),
                            dcc.Dropdown(
                                id="year-dropdown",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "75%",
                                }),
                        ],
                        style={
                            "width": "100%",
                            "color": "white"  # Set the text color to white
                        },
                    ),
                    html.Div(
                        children=[
                            html.Img(
                                id="word-cloud-image",
                                src=word_cloud_image)
                        ],
                        style={
                            "width": "100%",
                            "color": "white"  # Set the text color to white
                        },
                    ),
                    html.Div(
        children=[
                    dcc.Graph(
                        id="polarity-pie",
                        figure=go.Figure(
                            data=[go.Pie(
                                labels=["Positive", "Negative"],
                                values=[50, 50],
                                marker=dict(colors=["blue", "red"]),
                                hole=0.4
                            )],
                            layout=go.Layout(
                                autosize=True,
                            )
                        ),
                        style={"flex": "1", "height": "100%"}
                    ),
                    dcc.Graph(
                        id="subjectivity-pie",
                        figure=go.Figure(
                            data=[go.Pie(
                                labels=["Subjective", "Objective"],
                                values=[50, 50],
                                marker=dict(colors=["blue", "red"]),
                                hole=0.4
                            )],
                            layout=go.Layout(
                                autosize=True,
                            )
                        ),
                        style={"flex": "1", "height": "100%"}
                    ),
                            ],
                style={
                    "width": "100%",
                    "color": "white",  # Set the text color to white
                    "display": "flex",
                    "justifyContent": "space-evenly",
                    "alignItems": "center",
                },
            ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "justifyContent": "space-evenly",
                    "alignItems": "center",
                    "height": "50%",
                    "background": "#00001a",
                },
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id="example-graph",
                        figure=px.bar(x=word_count_df['word'], y=word_count_df['count'], labels={"x": "X", "y": "Y"}),
                        style={"width": "90%", "height": "100%"}
                    ),
                ],
                style={
                    "height": "55%",
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                },
            ),
        ],
        style={"height": "100vh", "display": "flex", "flexDirection": "column"},
    )
    return layout

def run_multi_article_analysis(articles):

    df = pd.DataFrame.from_dict(Counter(articles.split()), orient='index').reset_index()

    # Rename the columns
    df.columns = ['word', 'count']

    # Sort the dataframe by the count column
    df = df.sort_values(by='count', ascending=False)
    return df



