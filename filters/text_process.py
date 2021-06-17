from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer 
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
import pandas as pd
import math
from collections import Counter

from crawler.utils import connect_mongodb

df_train=pd.read_csv('filters/static/filters/fin_processed.csv')
DETECTION_THRESHOLD = 0.03

lemmatizer = WordNetLemmatizer()
vectorizer = CountVectorizer(max_features=1500)
classifier = MultinomialNB(alpha=0.01)

training_vectors = vectorizer.fit_transform(df_train.Contents)
classifier.fit(training_vectors, df_train.Labels)

# TODO(): Assign DETECTION_THRESHOLD and edit dataset fin_processed.csv

def detect_text(text):
    data = re.sub('[^\w\s]', '', text)
    data = data.lower()
    data = word_tokenize(data)
    data = [lemmatizer.lemmatize(word) for word in data if word not in set(stopwords.words('english'))]

    test_vectors = vectorizer.transform(data)

    predict = classifier.predict(test_vectors)

    ratio = float(format((sum(predict)/len(predict)), ".2f"))
    
    detected = ratio >= DETECTION_THRESHOLD

    print("\nRatio:", ratio)
    print("Detected", detected)

    return detected


# For content similarity ----->

def compare_page_content(text1):

    lemmatizer_custom = WordNetLemmatizer()

    text1 = re.sub('[^\w\s]', '', text1)
    text1 = text1.lower()
    text1 = word_tokenize(text1)
    text1 = [lemmatizer_custom.lemmatize(word) for word in text1 if word not in set(stopwords.words('english'))]
    counter1 = Counter(text1)

    databases = ['surfacedb']
    collections = ['seed-urls-visited']
    fields = ['seed-url']

    cs_matrix = []

    for database, collection, field in zip(databases, collections, fields):
        visited_coll = connect_mongodb(database, collection)
        for x in visited_coll.find():
            coll = connect_mongodb(database, x[field])

            for document in coll.find():
                try:
                    text2 = document["Page content"]
                    text2 = re.sub('[^\w\s]', '', text2)
                    text2 = text2.lower()
                    text2 = word_tokenize(text2)
                    text2 = [lemmatizer_custom.lemmatize(word) for word in text2 if word not in set(stopwords.words('english'))]

                    counter2 = Counter(text2)
                    terms = set(counter1).union(counter2)
                    dotproduct = sum(counter1.get(k, 0) * counter2.get(k, 0) for k in terms)
                    magnitude1 = math.sqrt(sum(counter1.get(k, 0)**2 for k in terms))
                    magnitude2 = math.sqrt(sum(counter2.get(k, 0)**2 for k in terms))

                    result = float(format(dotproduct / (magnitude1 * magnitude2) * 100, "0.4f"))
                    print(">>>>", result)

                    cs_matrix.append([document["Link"], result, database, x[field]])

                except Exception:
                    print(document["Link"], "invalid: Page content not found")

    cs_matrix = sorted(cs_matrix, key=lambda x : x[1])[::-1]
    
    return cs_matrix




