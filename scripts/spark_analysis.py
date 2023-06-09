from pyspark.sql.functions import regexp_replace, trim, expr
from pyspark.sql.types import FloatType, StringType, ArrayType, IntegerType, MapType
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.sql.functions import udf
from nltk.stem import WordNetLemmatizer
from pyspark.ml import Pipeline
import json
from collections import Counter
from textblob import TextBlob
import nltk
nltk.download('wordnet')
from nltk.corpus import stopwords as stop
nltk.download('stopwords')

# Analyze articles in spark
def analyze_articles():
    # Create spark session
    spark = SparkSession \
        .builder \
        .appName("sentiment_analysis") \
        .getOrCreate()

    # Load data into spark
    with open("temp/spark_input.json") as file:
        data = json.load(file)
    for row in data:
        row["_id"] = row["_id"]["$oid"] 
    df = spark.createDataFrame(data)

    # Define regular expression to match punctuation
    regex = r'[^A-Za-z0-9\s]+'
    # Remove punctuation and unwanted text from title
    df = df.withColumn("title", regexp_replace(df["title"], regex, ""))
    df = df.withColumn("title", regexp_replace(df["title"], "The New York Times", ""))
    df = df.withColumn("title", trim(df["title"]))
    # Remove punctuation from text
    df = df.withColumn("text", regexp_replace(df["content"], regex, ""))

    # Tokenize text
    tokenizer = Tokenizer(inputCol="text", outputCol="words")
    # Remove stop words from text
    stopwords = StopWordsRemover.loadDefaultStopWords("english") + [""] + stop.words()
    stop_words_remover = StopWordsRemover(inputCol=tokenizer.getOutputCol(), outputCol="filtered_words", stopWords=stopwords)
    # Create pipeline to apply tokenizer and stop words remover
    pipeline = Pipeline(stages=[tokenizer, stop_words_remover])
    df = pipeline.fit(df).transform(df)
    
    # Lemmatize words
    lemmatizer = WordNetLemmatizer()
    def lemmatize(words):
        return [lemmatizer.lemmatize(word) for word in words]
    lemmatize_udf = udf(lemmatize, ArrayType(StringType()))
    df = df.withColumn("lemmatized_words", lemmatize_udf(df.filtered_words))
    # Filter out short words
    df = df.withColumn("lemmatized_words", expr("filter(lemmatized_words, x -> not(length(x) < 3))"))
    
    # Create word count
    def count(words):
        return dict(Counter(words).most_common())
    count_udf = udf(count, MapType(StringType(), IntegerType()))
    df = df.withColumn("word_counts", count_udf(df.lemmatized_words))
   
    # Calculate subjectivity of article
    def polarity(words):
        text = " ".join(words)
        return TextBlob(text).sentiment.polarity
    polarity_udf = udf(polarity, FloatType())
    # Calculate polarity of article
    def subjectivity(words):
        text = " ".join(words)
        return TextBlob(text).sentiment.subjectivity
    subjectivity_udf = udf(subjectivity, FloatType())
    df = df.withColumn("polarity", polarity_udf(df.lemmatized_words))
    df = df.withColumn("subjectivity", subjectivity_udf(df.lemmatized_words))
   
    # Output analysis to json format
    articles = df.select(["_id", "title", "word_counts", "polarity", "subjectivity"]).toPandas()
    articles.to_json("temp/spark_output.json", orient="records")