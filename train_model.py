import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# LOAD DATA
df = pd.read_csv("whatsapp_sentiment_final.csv")

# 🔥 FIX: DROP EMPTY / NaN ROWS
df = df.dropna(subset=["clean_message"])
df = df[df["clean_message"].str.strip() != ""]

print("Cleaned dataset size:", len(df))

X = df["clean_message"].astype(str)
y = df["sentiment"]

# TF-IDF
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=7000,
    min_df=2
)

X_vec = vectorizer.fit_transform(X)

# TRAIN TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X_vec,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# TRAIN MODEL
model = MultinomialNB(alpha=0.3)
model.fit(X_train, y_train)

# EVALUATION
y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# SAVE MODEL
pickle.dump(model, open("sentiment_model.pkl", "wb"))
pickle.dump(vectorizer, open("tfidf_vectorizer.pkl", "wb"))

print("✅ Model and vectorizer saved successfully")
