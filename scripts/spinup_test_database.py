import pymongo
import csv

csv.field_size_limit(1000000)

client = pymongo.MongoClient('localhost', 27017)
# Drop NewsInfo database if it exists
client.drop_database("testNewsInfo")
db = client["testNewsInfo"]
articles = db["articles"]

files = ['data/articles1.csv']
for file in files:
    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Only load the first 15 articles
            if int(row['']) > 15:
                pass
            else:
                row['_id'] = int(row['id'])
                if row['year'] != '':
                    row['year'] = int(float(row['year']))
                    row['month'] = int(float(row['month']))
                    row['last_name'] = row['authors'].split(' ')[-1]
                    row['first_name'] = row['authors'].split(' ')[0]
                del row['id']
                del row['']
                articles.insert_one(row)

    # Close file
    csvfile.close()