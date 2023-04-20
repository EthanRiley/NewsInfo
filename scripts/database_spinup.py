from pymongo import MongoClient
import csv
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
from spark_analysis import analyze_articles

# Connect to mongo
client = MongoClient()
# Drop NewsInfo database if it exists
client.drop_database("NewsInfo")
db = client.NewsInfo
articles = db.articles
temp = db.temp

# Load articles from csv files into mongo
def insert_mongo(files):
    # Increase csv size limit
    csv.field_size_limit(1000000)
    # Limit input columns
    columns = ["title", "publication", "author", "year", "month", "date", "content", "url"]
    # Add articles from each file to database
    for file in files:
        with open(file, 'r', encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert row to dictionary
                row = {key: value for key, value in row.items() if key in columns}
                # Convert year to integer
                if row['year'] != '':
                    row['year'] = int(float(row['year']))
                # Convert month to integer
                if row['month'] != '':
                    row['month'] = int(float(row['month']))
                # Check that article contains all required values
                insert=True
                for col in columns[:7]:
                    if row[col] == "":
                        insert=False
                # Insert article to database
                if insert:
                    articles.insert_one(row)
        # Close file
        csvfile.close()
    
    # Save articles to json file for spark input
    cursor = articles.find()
    with open('temp/spark_input.json', 'w') as file:
        json.dump(json.loads(dumps(cursor)), file)

# Add analysis data to mongo
def add_to_mongo():
    # Load analysis data into temporary collection
    temp.drop()
    with open('temp/spark_output.json') as file:
        file_data = json.load(file)
    temp.insert_many(file_data)
    # Update articles collection by matching article ID
    for x in temp.find():
        articles.update_one({"_id":ObjectId(x["_id"])},
                            {"$set": {"title": x["title"],
                                      "word_counts":x["word_counts"],
                                      "polarity":x["polarity"],
                                      "subjectivity":x["subjectivity"]}})

if __name__ == "__main__":
    # Load all articles from dataset
    #files = ['data/articles1.csv', 'data/articles2.csv', 'data/articles3.csv']
    # Load an a sample of articles, recommended and sufficient for project viewing to avoid extra system setup for large data analysis in spark
    files = ["data/articles_sample2.csv"]
    # Load articles from files into mongo
    insert_mongo(files)
    # Analayze articles in spark
    analyze_articles()
    # Add analysis information to mongo
    add_to_mongo()
