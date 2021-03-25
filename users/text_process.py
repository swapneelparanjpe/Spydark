from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer 
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
import pandas as pd

df_train=pd.read_csv('users/static/users/fin_processed.csv')
detection_threshold = 0.30

lemmatizer = WordNetLemmatizer()
vectorizer = CountVectorizer(max_features=1500)
classifier = MultinomialNB(alpha=0.01)

training_vectors = vectorizer.fit_transform(df_train.Contents)
classifier.fit(training_vectors, df_train.Labels)

# TODO(): Assign detection_threshold and edit dataset fin_processed.csv

def detect_text(text):
    data = re.sub('[^\w\s]', '',text)
    data = data.lower()
    data = word_tokenize(data)
    data = [lemmatizer.lemmatize(word) for word in data if word not in set(stopwords.words('english'))]

    test_vectors = vectorizer.transform(data)

    predict = classifier.predict(test_vectors)

    ratio = float(format((sum(predict)/len(predict)), ".2f"))
    
    detected = ratio >= detection_threshold

    print("\nRatio:", ratio)
    print("Detected", detected)

    return detected


