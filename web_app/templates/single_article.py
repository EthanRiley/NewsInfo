import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import io
import matplotlib
matplotlib.use('agg')

# Create the single article search dashboard
def create_dashboard_component(article):
    # Convert the json of articles into a dataframe of word counts
    word_count_df = run_article_analysis(article)
    # Create the word cloud image
    word_cloud_image = create_word_cloud_image(word_count_df.set_index("word").to_dict()["count"])
    layout = html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            # Redirect to other dashboard
                            dcc.Link(html.Button("GO TO QUERY VIEW",
                                                 style={
                                                    "width": "25%",
                                                    "margin-bottom": "10px",
                                                    "background-color": "teal",
                                                    "border-radius": "12px",
                                                    "color": "white",
                                                    "padding": "10px",
                                                    "align": "right",
                                                    "text-align": "center",
                                                    "text-decoration": "none",
                                                    "display": "inline-block",
                                                    "font-size": "18px",
                                                    "cursor": "pointer"
                                                }
                                ), href='/dashagg', refresh=True),
                            # Article search bar
                            dcc.Dropdown(
                                id="article-selector",
                                placeholder="Select an article...",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "75%",
                                }),
                            # Single article metadata
                            html.H1(f"{article['title']}",
                                id="article-title"),
                            html.P(f"Author: {article['author']}",
                                id="article-author"),
                            html.P(f"Publication: {article['publication']}",
                                id='article-publication'),
                            html.P(f"Date: {article['date']}",
                                id='article-date'),
                            html.P(f"URL: {'N/a' if article['url'] == '' else article['url']}",
                                id='article-url'),
                            html.P(f"Polarity: {'Positive' if article['polarity'] > 0.01 else 'Negative' if article['polarity'] < -0.01 else 'Neutral'}",
                                id='article-polarity'),
                            html.P(f"Subjectivity: {'Subjective' if article['subjectivity'] > 0.55 else 'Objective' if article['subjectivity'] < 0.45 else 'Neutral'}",
                                id='article-subjectivity')
                            
                        ],
                        style={
                            "width": "50%",
                            "color": "white"  # Set the text color to white
                        },
                    ),
                    # Word cloud image
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
            # Word count graph
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
                    "alignItems": "center"
                },
            ),
        ],
        style={"height": "100vh", "display": "flex", "flexDirection": "column"},
    )
    return layout

# Get word counts for an individual article into a dataframe
def run_article_analysis(article):
    # Create a dataframe from the article where on column is the word and the other is the count
    df = pd.DataFrame.from_dict(article["word_counts"], orient='index').reset_index()
    # Rename the columns
    df.columns = ['word', 'count']
    # Sort the dataframe by the count column
    df = df.sort_values(by='count', ascending=False)
    # Choose the first 50 words
    df = df.head(50)
    return df

# Create a word count image from a dictionary of word counts
def create_word_cloud_image(word_counts):
    wordcloud = WordCloud(background_color='white', width=800, height=400).generate_from_frequencies(word_counts)

    # Convert the generated word cloud to an image
    buffer = io.BytesIO()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    image_data = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{image_data}'
