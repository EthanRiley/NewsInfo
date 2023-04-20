# NewsInfo
A Flask Web App built on top of MongoDB and Apache Spark for displaying news analytics
To run the application on your own machine:
1. Download the dataset from https://www.kaggle.com/datasets/snapcrack/all-the-news or use the sample provided in the data folder (recommended to avoid the need to setup your system for large data analysis in spark, and requires that the input files in database_spinup.py are changed by uncommenting a single line or code). If your having trouble with the setup required for large data analysis in spark, contact us.
2. Start your mongo server using mongod from the mongo server bin or equivalent
3. run scripts/database_spinup.py to load the data into mongo database
4. run app.py to initialize the web app and go to http://127.0.0.1:5000/ to view the dashboards
