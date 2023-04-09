import pymongo
import csv

csv.field_size_limit(1000000)

client = pymongo.MongoClient('localhost', 27017)
# Drop NewsInfo database if it exists
client.drop_database("NewsInfo")
db = client["NewsInfo"]
articles = db["articles"]

files = ['data/articles1.csv', 'data/articles2.csv', 'data/articles3.csv']
for file in files:
    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['_id'] = int(row['id'])
            del row['id']
            del row['']
            articles.insert_one(row)

    # Close file
    csvfile.close()