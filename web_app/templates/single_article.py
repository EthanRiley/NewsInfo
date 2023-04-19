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
import matplotlib
matplotlib.use('agg')

def create_dashboard_component(article):
    word_count_df = run_article_analysis(article)
    word_cloud_image = create_word_cloud_image(word_count_df["word"])
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
                            html.H1(f"{article['title']}",
                                id="article-title"),
                            html.P(f"Author: {article['author']}",
                                id="article-author"),
                            html.P(f"Publication: {article['publication']}",
                                id='article-publication'),
                            html.P(f"Date: {article['date']}",
                                id='article-date'),
                            html.P(f"URL: {'N/A' if article['url'] == '' else article['url']}",
                                id='article-url')
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
                        figure=px.bar(x=word_count_df['word'], y=word_count_df['count'], labels={"x": "Count", "y": "Words"}),
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
    df = df[df["count"] > 1]
    df = df.sort_values(by='count', ascending=False)
    return df

def create_word_cloud_image(article_text):
    article_text = " ".join(article_text)
    #print(article_text[:100])
    wordcloud = WordCloud(background_color='white', width=800, height=400).generate(article_text)

    # Convert the generated word cloud to an image
    buffer = io.BytesIO()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    image_data = base64.b64encode(buffer.getvalue()).decode()

    return f'data:image/png;base64,{image_data}'
