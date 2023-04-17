from flask import Flask, jsonify
from flask_pymongo import PyMongo
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, render_template
import pandas as pd
from templates.single_article import create_dashboard_component, run_article_analysis, create_word_cloud_image
from dash.dependencies import Input, Output
import requests
import plotly.express as px
 
# Initialize the Flask app
app = Flask(__name__)

# Initialize the Dash app with the Flask app as its server
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

# Load the data
app.config['MONGO_URI'] = 'mongodb://localhost:27017/testNewsInfo'
mongo = PyMongo(app)


#@app.route("/dash")
#def dash():
    #return render_template("page.html")

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/articles")
def article_full():
    articles = mongo.db.articles.find()
    article_list = [article for article in articles]
    
    for article in article_list:
        # Convert ObjectId to string to make it JSON serializable
        article['_id'] = str(article['_id'])
    
    return jsonify(article_list)

@app.route("/articlenames")
def articlenames():
    articles = mongo.db.articles.find()
    article_list = [article['title'] for article in articles]
    
    return article_list


@app.route("/articles/one")
def article_one():
    articles = mongo.db.articles.find_one({"_id": 17283})
    # Convert the MongoDB cursor to a list of dictionaries
    return articles



@app.route("/articles/single/<string:article_id>")
def get_article(article_id):
    article = mongo.db.articles.find_one({"_id": int(article_id)})
    # Convert the MongoDB cursor to a list of dictionaries
    return article

@app.route("/articles/query/<string:year>")
def get_article_year(year):
    articles = mongo.db.articles.find({"year": int(year)})
    article_list = [article for article in articles]
    
    for article in article_list:
        # Convert ObjectId to string to make it JSON serializable
        article['_id'] = str(article['_id'])
    
    return jsonify(article_list)

@app.route("/articles/query/<string:year>/<string:month>")
def get_article_year_month(year, month):
    articles = mongo.db.articles.find({"year": int(year), "month": int(month)})
    article_list = [article for article in articles]
    
    for article in article_list:
        # Convert ObjectId to string to make it JSON serializable
        article['_id'] = str(article['_id'])
    
    return jsonify(article_list)

@app.route("/articles/query/<string:author>")
def get_article_author(author):
    articles = mongo.db.articles.find({"authors": author})
    article_list = [article for article in articles]
    
    for article in article_list:
        # Convert ObjectId to string to make it JSON serializable
        article['_id'] = str(article['_id'])
    
    return jsonify(article_list)

dash_app.layout = create_dashboard_component(article_one())

@dash_app.callback(
    Output("article-selector", "options"),
    Output("article-selector", "value"),
    Input("article-selector", "search_value"))
def update_article_options(search_value):
    if search_value is None:
        
        search_value = ''

    response = requests.get(f"http://127.0.0.1:5000/articles")
    
    articles = response.json()
    # Filter the article_names based on the search_value
    filtered_article_names = [{"label": article['title'], "value":article['_id']} for article in articles if search_value.lower() in article['title'].lower()]

    # Create options for the dropdown menu using the fetched article data
    #options = [{"label": name, "value": idx} for idx, name in enumerate(filtered_article_names)]

    # Set the default selected value to the first option in the list
    default_value = filtered_article_names[0]["value"] if filtered_article_names else None

    return filtered_article_names, default_value

@dash_app.callback(
    Output("example-graph", "figure"),
    Output("word-cloud-image", "src"),
    Input("article-selector", "value"),
)
def update_content(selected_article_index):
    if selected_article_index is None:
        return dash.no_update, dash.no_update

    response = requests.get(f"http://127.0.0.1:5000/articles/single/{selected_article_index}")
    article = response.json()
    

    word_count_df = run_article_analysis(article)
    word_cloud_image = create_word_cloud_image(article["content"])

    updated_graph = px.bar(
        x=word_count_df["word"],
        y=word_count_df["count"],
        labels={"x": "X", "y": "Y"},
    )

    return updated_graph, word_cloud_image

if __name__ == "__main__":
    app.run(threaded=True)
