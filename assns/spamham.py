# -*- coding: utf-8 -*-
"""SpamHam.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EcN6QqnCzEXA5zJ81LSpHGuvDssfk1yB
"""

!pip install gensim
!pip install fasttext
!pip install xgboost
!pip install catboost
!pip install lightgbm
!pip install wordcloud

import pandas as pd
import numpy as np
import nltk
import gensim
import tensorflow as tf
import re
import scipy
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from gensim.models import KeyedVectors, Word2Vec
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Flatten

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt_tab')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

df = pd.read_csv("/content/spam.csv", encoding="latin-1")
df = df.dropna(how="any", axis=1)
df.columns = ['target', 'message']
df.head()

def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text).lower()  # Remove punctuation and lowercase
    text = re.sub('\[.*?\]', '', text)  # Remove text in square brackets
    text = re.sub('https?://\S+|www\.\S+', '', text)  # Remove links
    text = re.sub('\w*\d\w*', '', text) # Remove words containing numbers
    words = nltk.word_tokenize(text) # Tokenize
    words = [w for w in words if w not in stop_words] # Remove stopwords
    words = [lemmatizer.lemmatize(w) for w in words] # Lemmatize
    return " ".join(words)

df['processed_message'] = df['message'].apply(preprocess_text)

df.head()

le = LabelEncoder()
le.fit(df['target'])
df['target_encoded'] = le.transform(df['target'])
df.head()

plt.figure(figsize=(8, 6))
sns.countplot(x='target', data=df)
plt.title('Distribution of Target Variable')
plt.show()

df['message_length'] = df['message'].apply(len)
plt.figure(figsize=(8, 6))
sns.histplot(df['message_length'], kde=True)
plt.title('Distribution of Message Lengths')
plt.show()

text = " ".join(df['processed_message'].tolist())
wordcloud = WordCloud(width=800, height=400).generate(text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud)
plt.axis("off")
plt.title('Word Cloud of Processed Messages')
plt.show()

x = df['processed_message']
y = df['target_encoded']
print("Shape of Data:")
print(len(x), len(y))
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=42)
print("Shape of Train:")
print(len(x_train), len(y_train))
print("Shape of Test:")
print(len(x_test), len(y_test))

!wget http://nlp.stanford.edu/data/glove.6B.zip
!unzip glove.6B.zip
!pip install fasttext
import fasttext

#Countvectorisor
vectorizer = CountVectorizer()
x_train_vec = vectorizer.fit_transform(x_train)
x_test_vec = vectorizer.transform(x_test)

# TF-IDF
tfidf_vectorizer = TfidfVectorizer()
x_train_tfidf = tfidf_vectorizer.fit_transform(x_train)
x_test_tfidf = tfidf_vectorizer.transform(x_test)

# Word2Vec
# Train Word2Vec model
tokenized_messages = [nltk.word_tokenize(text) for text in x_train]
word2vec_model = Word2Vec(sentences=tokenized_messages, vector_size=100, window=5, min_count=1, workers=4)

# Function to create sentence embeddings
def get_sentence_embedding(sentence):
    words = nltk.word_tokenize(sentence)
    vectors = [word2vec_model.wv[word] for word in words if word in word2vec_model.wv]
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return np.zeros(100)  # Return zero vector if no words are in vocabulary

x_train_word2vec = np.array([get_sentence_embedding(sentence) for sentence in x_train])
x_test_word2vec = np.array([get_sentence_embedding(sentence) for sentence in x_test])

# Load pre-trained GloVe embeddings
glove_file = '/content/glove.6B.100d.txt' # Replace with your path
glove_model = {}
with open(glove_file, encoding='utf-8') as f:
    for line in f:
        values = line.split()
        word = values[0]
        vector = np.asarray(values[1:], dtype='float32')
        glove_model[word] = vector

# Function to get sentence embedding using GloVe
def get_glove_embedding(sentence):
    words = nltk.word_tokenize(sentence)
    vectors = [glove_model.get(word, np.zeros(100)) for word in words] # Use zeros if word not found
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return np.zeros(100)

x_train_glove = np.array([get_glove_embedding(sentence) for sentence in x_train])
x_test_glove = np.array([get_glove_embedding(sentence) for sentence in x_test])

with open('train.txt', 'w') as f:
  for text, label in zip(x_train, y_train):
    f.write(f"__label__{label} {text}\n")

fasttext_model = fasttext.train_supervised('train.txt', epoch=25)
def get_fasttext_embedding(text):
    return fasttext_model.get_sentence_vector(text)

x_train_fasttext = np.array([get_fasttext_embedding(sentence) for sentence in x_train])
x_test_fasttext = np.array([get_fasttext_embedding(sentence) for sentence in x_test])

models = {
    "XGBoost": XGBClassifier(),
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(),
    "SVM": SVC(),
    "Random Forest": RandomForestClassifier(),
    "KNN": KNeighborsClassifier(),
    "Catboost": CatBoostClassifier(verbose=0),
    #"LightGBM": LGBMClassifier()
}

dataset = {
    'countvectorizer': {
        'train': x_train_vec,
        'test': x_test_vec
    },
    'tfidf': {
        'train': x_train_tfidf,
        'test': x_test_tfidf
    },
    'word2vec': {
        'train': x_train_word2vec,
        'test': x_test_word2vec
    },
    'glove': {
        'train': x_train_glove,
        'test': x_test_glove
    },
    'fasttext': {
        'train': x_train_fasttext,
        'test': x_test_fasttext
    }
}

def train_and_evaluate_naive_bayes(x_train, x_test, y_train, y_test, dataset_name):
    # Convert sparse matrices to dense arrays before clipping
    if isinstance(x_train, (scipy.sparse.csr_matrix, scipy.sparse.csc_matrix)):
        x_train = x_train.toarray()
    if isinstance(x_test, (scipy.sparse.csr_matrix, scipy.sparse.csc_matrix)):
        x_test = x_test.toarray()

    x_train_clipped = np.clip(x_train, 0, None)
    x_test_clipped = np.clip(x_test, 0, None)

    nb_classifier = MultinomialNB()
    nb_classifier.fit(x_train_clipped, y_train)
    nb_pred = nb_classifier.predict(x_test_clipped)
    nb_accuracy = accuracy_score(y_test, nb_pred)
    nb_precision = precision_score(y_test, nb_pred)
    nb_recall = recall_score(y_test, nb_pred)
    print(f"Naive Bayes ({dataset_name}) Accuracy: {nb_accuracy}")
    return nb_accuracy, nb_precision, nb_recall

results = []
for dataset_name, data in dataset.items():
    accuracy, precision, recall = train_and_evaluate_naive_bayes(data['train'], data['test'], y_train, y_test, dataset_name)
    results.append([dataset_name, accuracy, precision, recall])

df_results = pd.DataFrame(results, columns=['Dataset', 'Accuracy', 'Precision', 'Recall'])
df_results

df_results2=[]
for model_name, model in models.items():
    for dataset_name, data in dataset.items():
        print(f"Training {model_name} on {dataset_name} dataset...")
        try:
            model.fit(data['train'], y_train)
            y_pred = model.predict(data['test'])
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            print(f"{model_name} on {dataset_name}: Accuracy = {accuracy}")
            df_results2.append({
                'Model': model_name,
                'Dataset': dataset_name,
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall
            })
        except ValueError as e:
            print(f"Error training {model_name} on {dataset_name}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

df_results2 = pd.DataFrame(df_results2)
df_results2

ann_results=[]
for dataset_name, data in dataset.items():
    print(f"Training ANN on {dataset_name} dataset...")
    try:
        if dataset_name == 'countvectorizer':
            x_train_data = x_train_vec
            x_test_data = x_test_vec
        elif dataset_name == 'tfidf':
            input_shape = (x_train_tfidf.shape[1],)
            x_train_data = x_train_tfidf.toarray()
            x_test_data = x_test_tfidf.toarray()
        else:
            input_shape = (x_train_word2vec.shape[1],)
            if dataset_name == 'word2vec':
              x_train_data = x_train_word2vec
              x_test_data = x_test_word2vec
            elif dataset_name == 'glove':
              x_train_data = x_train_glove
              x_test_data = x_test_glove
            elif dataset_name == 'fasttext':
              x_train_data = x_train_fasttext
              x_test_data = x_test_fasttext

        ann_model = Sequential([
            Dense(64, activation='relu', input_shape=(x_train_data.shape[1],)),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])

        ann_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        ann_model.fit(x_train_data, y_train, epochs=5, batch_size=32, verbose=0)
        _, ann_accuracy = ann_model.evaluate(x_test_data, y_test, verbose=0)
        ann_precision = precision_score(y_test, (ann_model.predict(x_test_data) > 0.5).astype("int32"))
        ann_recall = recall_score(y_test, (ann_model.predict(x_test_data) > 0.5).astype("int32"))
        ann_results.append({
            'Model': 'ANN',
            'Dataset': dataset_name,
            'Accuracy': ann_accuracy,
            'Precision': ann_precision,
            'Recall': ann_recall
        })
        print(f"ANN ({dataset_name}) Accuracy: {ann_accuracy}")
    except ValueError as e:
        print(f"Error training ANN on {dataset_name}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

dfann=pd.DataFrame(ann_results)
dfann

ResultsData=pd.concat([df_results,df_results2,dfann])
ResultsData

