from flask import Flask, jsonify, redirect
from flask_pymongo import PyMongo
import dash
from flask import Flask, render_template
from templates.single_article import create_dashboard_component, run_article_analysis, create_word_cloud_image
from templates.article_aggregation import create_agg_dashboard_component, run_multi_article_analysis, graph_pie
from dash.dependencies import Input, Output, State
import requests
import plotly.express as px
from bson.objectid import ObjectId

# Initialize the Flask app idk why this wpnt let mepush
app = Flask(__name__)

# Initialize the Dash app with the Flask app as its server
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

# Initialize another Dash app with the flask app as its server
dash_app_agg = dash.Dash(__name__, server=app, url_base_pathname='/dashagg/')

# Load the data
app.config['MONGO_URI'] = 'mongodb://localhost:27017/NewsInfo'
mongo = PyMongo(app)

# Routes to the homepage
@app.route("/")
def homepage():
    # Redirect the homepage to the new homepage (one of the dashboards)
    return redirect("http://127.0.0.1:5000/dash")
    # Old homepage
    return render_template("homepage.html")

# Route to obtain all articles
@app.route("/articles")
def article_full():
    article_list = [article for article in mongo.db.articles.find()]
    # Convert ObjectId to string to make it JSON serializable
    for article in article_list:
        article['_id'] = str(article['_id'])
    return jsonify(article_list)

# Route to obtain all article names
@app.route("/articlenames")
def articlenames():
    article_list = [article['title'] for article in mongo.db.articles.find()]
    return article_list

# Route to obtain one article as defailt
@app.route("/articles/one")
def article_one():
    article = mongo.db.articles.find_one()
    # Convert ObjectId to string to make it JSON serializable
    article["_id"] = str(article["_id"])
    return article

# Route to obtain a single article based on ID
@app.route("/articles/single/<string:article_id>")
def get_article(article_id):
    article = mongo.db.articles.find_one({"_id": ObjectId(article_id)})
    # Convert ObjectId to string to make it JSON serializable
    article["_id"] = str(article["_id"])
    return article

# Route to query articles by year
@app.route("/articles/query/<string:year>")
def get_article_year(year):
    articles = mongo.db.articles.find({"year": int(year)})
    article_list = [article for article in articles]
    # Convert ObjectId to string to make it JSON serializable
    for article in article_list:
        article['_id'] = str(article['_id'])
    return jsonify(article_list)

# Route to query articles by year and month
@app.route("/articles/query/<string:year>/<string:month>")
def get_article_year_month(year, month):
    articles = mongo.db.articles.find({"year": int(year), "month": int(month)})
    article_list = [article for article in articles]
    # Convert ObjectId to string to make it JSON serializable
    for article in article_list:
        article['_id'] = str(article['_id'])
    return jsonify(article_list)

# Route to query articles by author
@app.route("/articles/query/author/<string:author>")
def get_article_author(author):
    author = author.replace("%20", " ")
    articles = mongo.db.articles.find({"author": author})
    article_list = [article for article in articles]
    # Convert ObjectId to string to make it JSON serializable
    for article in article_list:
        article['_id'] = str(article['_id'])
    return jsonify(article_list)

# Route to obtain all distinct publications
@app.route("/publications")
def get_publications():
    publications = mongo.db.articles.distinct("publication")
    return jsonify(publications)

# Route to obtain all distinct authors
@app.route("/authors")
def get_authors():
    authors = mongo.db.articles.distinct("author")
    return jsonify(authors)

# Route to obtain all distinct months
@app.route("/months")
def get_months():
    months = sorted(list(set(mongo.db.articles.distinct("month"))))
    return jsonify(months)

# Route to obtain all distinct years
@app.route("/years")
def get_years():
    years = sorted(list(set(mongo.db.articles.distinct("year"))))
    return jsonify(years)

# Create dashboard layouts
dash_app.layout = create_dashboard_component(article_one())
with app.app_context():
    dash_app_agg.layout = create_agg_dashboard_component(article_full().json)

# Callback for updating search options
@dash_app.callback(
    Output("article-selector", "options"),
    Output("article-selector", "value"),
    Input("article-selector", "search-value"))
def update_article_options(search_value):
    if search_value is None:
       search_value = ''
    # Get all artticles
    response = requests.get(f"http://127.0.0.1:5000/articles")
    articles = response.json()
    # Filter the article_names based on the search_value
    filtered_article_names = [{"label": article['title'], "value":str(article['_id'])} for article in articles if search_value.lower() in article['title'].lower()]
    # Set the default selected value to the first option in the list
    default_value = filtered_article_names[0]["value"] if filtered_article_names else None

    return filtered_article_names, default_value

@dash_app.callback(
    Output("example-graph", "figure"),
    Output("word-cloud-image", "src"),
    Output("article-title", "children"),
    Output("article-author", "children"),
    Output("article-publication", "children"),
    Output("article-date", "children"),
    Output("article-url", "children"),
    Output("article-polarity", "children"),
    Output("article-subjectivity", "children"),
    Input("article-selector", "value"),
)
def update_content(selected_article_index):
    if selected_article_index is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    response = requests.get(f"http://127.0.0.1:5000/articles/single/{selected_article_index}")
    article = response.json()
    word_count_df = run_article_analysis(article)
    word_cloud_image = create_word_cloud_image(word_count_df.set_index("word").to_dict()["count"])

    updated_graph = px.bar(
        x=word_count_df["word"],
        y=word_count_df["count"],
        labels={"x": "Word", "y": "Count"},
    )
    url = 'N/a' if article['url'] == '' else article['url']
    polarity = f"Polarity: {'Positive' if article['polarity'] > 0.01 else 'Negative' if article['polarity'] < -0.01 else 'Neutral'}"
    subjectivity = f"Subjectivity: {'Subjective' if article['subjectivity'] > 0.55 else 'Objective' if article['subjectivity'] < 0.45 else 'Neutral'}"
    return updated_graph, word_cloud_image, article["title"], \
        f"Author: {article['author']}", f"Publication: {article['publication']}", \
        f"Date: {article['date']}", f"URL: {url}", polarity, subjectivity

# Define a function to fetch data from the server
def fetch_data():
    publications = requests.get("http://127.0.0.1:5000/publications").json()
    authors = requests.get("http://127.0.0.1:5000/authors").json()
    months = requests.get("http://127.0.0.1:5000/months").json()
    years = requests.get("http://127.0.0.1:5000/years").json()

    return publications, authors, months, years


# Callback to populate the dropdowns
@dash_app_agg.callback(
    Output("publication-dropdown", "options"),
    Output("author-dropdown", "options"),
    Output("month-dropdown", "options"),
    Output("year-dropdown", "options"),
    Input("publication-dropdown", "search_value"),
    Input("author-dropdown", "search_value"),
    Input("month-dropdown", "search_value"),
    Input("year-dropdown", "search_value"),
)
def update_dropdown_options(pub_search_value, auth_search_value, month_search_value, year_search_value):
    if not any([pub_search_value, auth_search_value, month_search_value, year_search_value]):
        pub_search_value = auth_search_value = month_search_value = year_search_value = ''

    publications, authors, months, years = fetch_data()

    publication_options = [{"label": pub, "value": pub} for pub in publications if pub_search_value.lower() in pub.lower()]
    author_options = [{"label": author, "value": author} for author in authors if auth_search_value.lower() in author.lower()]
    month_options = [{"label": month, "value": month} for month in months if month_search_value.lower() in str(month)]
    year_options = [{"label": year, "value": year} for year in years if year_search_value.lower() in str(year)]

    return publication_options, author_options, month_options, year_options

def generate_query(publication, author, month, year):
    query = {"publication": publication, "author": author, "month": month, "year": year}
    query = {key: value for key, value in query.items() if value != None}
    articles = mongo.db.articles.find(query)
    article_list = [article for article in articles]
    #for article in article_list:
        # Convert ObjectId to string to make it JSON serializable
      #  article['_id'] = str(article['_id'])
    
    return article_list

@dash_app_agg.callback(
    Output("example-graph", "figure"),
    Output("word-cloud-image", "src"),
    Output("query-message", "children"),
    Output("query-message", "style"),
    Output("polarity-pie", "figure"),
    Output("subjectivity-pie", "figure"),
    Input("query-button", "n_clicks"),
    State("publication-dropdown", "value"),
    State("author-dropdown", "value"),
    State("month-dropdown", "value"),
    State("year-dropdown", "value"),
)
def update_graphs_and_wordcloud(n_clicks, publication, author, month, year):
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    article_list = generate_query(publication, author, month, year)
    if len(article_list) == 0:
        return dash.no_update, dash.no_update, "No articles in selection, try again.", \
            {"color": "red", "margin-left": "10%"}, dash.no_update, dash.no_update
    word_count_df = run_multi_article_analysis(article_list)
    word_cloud_image = create_word_cloud_image(word_count_df.set_index("word").to_dict()["count"])

    updated_graph = px.bar(
        x=word_count_df["word"],
        y=word_count_df["count"],
        labels={"x": "Word", "y": "Count"},
    )
    if len(article_list) == 1:
        msg = "There is 1 article in the query."
    else:
        msg = f"There are {len(article_list)} articles in the query."

    return updated_graph, word_cloud_image, msg, \
        {"color": "white", "margin-left": "10%"}, \
        graph_pie(article_list, ["Positive", "Neutral", "Negative"], "polarity", -0.01, 0.01), \
        graph_pie(article_list, ["Subjective", "Neutral", "Objective"], "subjectivity", 0.45, 0.55)

if __name__ == "__main__":
    app.run(threaded=True)
