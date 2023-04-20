from pymongo import MongoClient
import csv
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
from spark_analysis import analyze_articles

client = MongoClient()
# Drop NewsInfo database if it exists
client.drop_database("NewsInfo")
db = client.NewsInfo
articles = db.articles
temp = db.temp

# Insert articles from csv files into mongo
def insert_mongo(files):
    csv.field_size_limit(1000000)
    columns = ["title", "publication", "author", "date", "year", "month", "url", "content"]
    for file in files:
        with open(file, 'r', encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row = {key: value for key, value in row.items() if key in columns}
                if row['year'] != '':
                    row['year'] = int(float(row['year']))
                if row['month'] != '':
                    row['month'] = int(float(row['month']))
                articles.insert_one(row)
        # Close file
        csvfile.close()
    cursor = articles.find()
    with open('temp/spark_input.json', 'w') as file:
        json.dump(json.loads(dumps(cursor)), file)

def add_to_mongo():
    temp.drop()
    with open('temp/spark_output.json') as file:
        file_data = json.load(file)
    temp.insert_many(file_data)
    for x in temp.find():
        articles.update_one({"_id":ObjectId(x["_id"])},
                            {"$set": {"title": x["title"],
                                      "word_counts":x["word_counts"],
                                      "polarity":x["polarity"],
                                      "subjectivity":x["subjectivity"]}})

if __name__ == "__main__":
    files = ["data/articles_sample2.csv"]
    #files = ['data/articles1.csv']#, 'data/articles2.csv', 'data/articles3.csv']
    insert_mongo(files)
    analyze_articles()
    add_to_mongo()
