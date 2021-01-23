from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer 
import re

lemmatizer = WordNetLemmatizer()

def detect_text(text):
    data = re.sub('[^\w\s]', '',text)
    data = data.lower()
    data = word_tokenize(data)
    data = [lemmatizer.lemmatize(word) for word in data if word not in set(stopwords.words('english'))]
    print(">>>", data)
    return data