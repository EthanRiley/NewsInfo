from flask import Flask, jsonify
from flask_pymongo import PyMongo
import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, render_template
import pandas as pd
 
# Initialize the Flask app
app = Flask(__name__)

# Initialize the Dash app with the Flask app as its server
#dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/')

# Load the data
app.config['MONGO_URI'] = 'mongodb://localhost:27017/testNewsInfo'
mongo = PyMongo(app)


#@app.route("/dash")
#def dash():
    #return render_template("page.html")

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/articles/one")
def articles():
    articles = mongo.db.articles.find_one({"_id": 17283})
    # Convert the MongoDB cursor to a list of dictionaries
    return articles

@app.route("/articles/<string:article_id>")
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

if __name__ == "__main__":
    app.run(threaded=True)
