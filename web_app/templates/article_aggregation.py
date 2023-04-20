import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from templates.single_article import create_word_cloud_image
import plotly.graph_objs as go

# Create the article query dashboard
def create_agg_dashboard_component(articles):
    # Convert the json of articles into a dataframe of word counts
    word_count_df = run_multi_article_analysis(articles)
    # Create the word cloud image
    word_cloud_image = create_word_cloud_image(word_count_df.set_index("word").to_dict()["count"])
    layout = html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            # Redirect to other dashboard
                            dcc.Link(html.Button("GO TO SEARCH VIEW",
                                                 style={
                                                    "width": "40%",
                                                    "margin-bottom": "10px",
                                                    "margin-left": "5%",
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
                                ), href='/dash', refresh=True),
                            # Article query options and information
                            html.H1("Query Database Articles:",
                                    style={
                                        "margin-left": "5%"
                                    }),
                            dcc.Dropdown(
                                id="publication-dropdown",
                                placeholder="Select a publication...",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "90%",
                                    "margin-top": "5px",
                                    "margin-left": "5%"
                                }),
                            dcc.Dropdown(
                                id="author-dropdown",
                                placeholder="Select an author...",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "90%",
                                    "margin-top": "5px",
                                    "margin-left": "5%"
                                }),
                            dcc.Dropdown(
                                id="month-dropdown",
                                placeholder="Select a release month...",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "90%",
                                    "margin-top": "5px",
                                    "margin-left": "5%"
                                }),
                            dcc.Dropdown(
                                id="year-dropdown",
                                placeholder="Select a release year...",
                                options=[],
                                style={
                                    "color": "black",
                                    "align": "left",
                                    "width": "90%",
                                    "margin-top": "5px",
                                    "margin-left": "5%"
                                }),
                            html.Button(
                                "QUERY",
                                id="query-button",
                                style={
                                    "width": "15%",
                                    "margin-top": "10px",
                                    "margin-left": "75%",
                                    "background-color": "teal",
                                    "border": "none",
                                    "border-radius": "12px",
                                    "color": "white",
                                    "padding": "10px",
                                    "align": "right",
                                    "text-align": "center",
                                    "text-decoration": "none",
                                    "display": "inline-block",
                                    "font-size": "18px",
                                    "cursor": "pointer"
                                },
                            ),
                            html.H2(
                                f"There are {len(articles)} articles in the query.",
                                id="query-message",
                                style={
                                    "color": "white",
                                    "margin-left": "10%"
                                }
                            )
                        ],
                        style={
                            "width": "100%",
                            "color": "white"  # Set the text color to white
                        },
                    ),
                    html.Div(
                        children=[
                            # Word cloud image
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
                            # Sentiment analysis graphs
                            dcc.Graph(
                                id="polarity-pie",
                                figure = graph_pie(articles, ["Positive", "Neutral", "Negative"],
                                                   "polarity", -0.01, 0.01),
                                style={"flex": "1", "height": "100%"}
                            ),
                            dcc.Graph(
                                id="subjectivity-pie",
                                figure = graph_pie(articles, ["Subjective", "Neutral", "Objective"],
                                                   "subjectivity", 0.45, 0.55),
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
                    # Word count graph
                    dcc.Graph(
                        id="example-graph",
                        figure=px.bar(x=word_count_df['word'], y=word_count_df['count'], labels={"x": "Word", "y": "Count"}),
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

# Graphs a pie chart using a list of articles and a selected field which contains a numeric value
# for cutoffs to be applied to for categories
def graph_pie(articles, labels, field, lower_cutoff, upper_cutoff):
    return go.Figure(data=[go.Pie(
                            labels=labels,
                            values=score_proportion(articles, field, lower_cutoff, upper_cutoff),
                            marker=dict(colors=["#1971E1", "#6D6A69", "#EF2929"]),
                            hole=0.4
                        )],
                    layout=go.Layout(
                        autosize=True,
                        )
                    )

# Determiens the count of articles in a category based on a numeric field and cutoffs
def score_proportion(articles, field, lower_cutoff, upper_cutoff):
    pos = len([1 for article in articles if article[field] > upper_cutoff])
    neg = len([1 for article in articles if article[field] < lower_cutoff])
    neu = len(articles) - pos - neg
    return [pos, neu, neg]


# Get word counts for a list of articles into a datafarame
def run_multi_article_analysis(articles):
    # Combine the dataframes
    df = pd.concat([pd.DataFrame.from_dict(article["word_counts"], orient='index') for article in articles]) 
    df.reset_index(inplace=True)
    # Rename the columns
    df.columns = ['word', 'count']
    # Group by word and sum
    df = df.groupby("word").sum()
    df.reset_index(inplace=True)
    # Sort the dataframe by the count column
    df = df.sort_values(by='count', ascending=False)
    # Choose the first 50 words
    df = df.head(50)
    return df



