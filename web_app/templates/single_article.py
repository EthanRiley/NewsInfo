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

def create_dashboard_component(article):
    word_count_df = run_article_analysis(article)
    word_cloud_image = create_word_cloud_image(article["content"])
    layout = html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            dcc.Dropdown(
                                id="article-selector",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "75%",
                                }),
                            html.H1(
                                id="article-title"),
                            html.P(
                                id="article-athor"),
                            html.P(
                                id='article-publication'),
                        ],
                        style={
                            "width": "50%",
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
                            "width": "40%",
                            "color": "white"  # Set the text color to white
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "justifyContent": "center",
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

def run_article_analysis(article):
    # Create a dataframe from the article where on column is the word and the other is the count
    df = pd.DataFrame.from_dict(article["word_counts"], orient='index').reset_index()

    # Rename the columns
    df.columns = ['word', 'count']

    # Sort the dataframe by the count column
    df = df.sort_values(by='count', ascending=False)
    return df

def create_word_cloud_image(article_text):
    wordcloud = WordCloud(background_color='white', width=800, height=400).generate(article_text)

    # Convert the generated word cloud to an image
    buffer = io.BytesIO()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_data = base64.b64encode(buffer.getvalue()).decode()

    return f'data:image/png;base64,{image_data}'
