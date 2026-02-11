import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


def train_and_save_model():
    # LOAD DATA
    df = pd.read_csv("../whatsapp_sentiment_final.csv")

    # CLEAN EMPTY ROWS
    df = df.dropna(subset=["clean_message"])
    df = df[df["clean_message"].str.strip() != ""]
    df["clean_message"] = df["clean_message"].astype(str)

    print("Cleaned dataset size:", len(df))

    X = df["clean_message"]
    y = df["sentiment"]

    # TF-IDF
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=12000,
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

    # MODEL
    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # EVALUATION
    y_pred = model.predict(X_test)

    print("\nAccuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # SAVE MODEL
    pickle.dump(model, open("sentiment_logistic.pkl", "wb"))
    pickle.dump(vectorizer, open("tfidf_logistic.pkl", "wb"))

    print("✅ Logistic Regression model saved")

    return model, vectorizer
