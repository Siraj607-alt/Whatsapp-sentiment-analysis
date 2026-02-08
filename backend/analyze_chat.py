import re
import pickle
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

nltk.download("stopwords")

# LOAD LOGISTIC REGRESSION MODEL
model = pickle.load(open("sentiment_logistic.pkl", "rb"))
vectorizer = pickle.load(open("tfidf_logistic.pkl", "rb"))

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

# TEXT CLEANING (SAME AS TRAINING)
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return " ".join(words)

def analyze_whatsapp_chat(file_path):
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    messages = []
    for line in lines:
        if " - " in line and ":" in line:
            try:
                msg = re.split(r" - .*?: ", line, maxsplit=1)[1].strip()
                if msg and "<Media omitted>" not in msg:
                    messages.append(msg)
            except:
                pass

    clean_msgs = [clean_text(m) for m in messages]
    vectors = vectorizer.transform(clean_msgs)

    # 🔥 PROBABILITY-BASED PREDICTION (KEY FIX)
    probs = model.predict_proba(vectors)
    classes = model.classes_

    predictions = []
    confidences = []

    for prob in probs:
        prob_dict = dict(zip(classes, prob))

        # confidence-based decision logic
        if prob_dict.get("Negative", 0) >= 0.40:
            predictions.append("Negative")
            confidences.append(prob_dict["Negative"])
        elif prob_dict.get("Positive", 0) >= 0.45:
            predictions.append("Positive")
            confidences.append(prob_dict["Positive"])
        else:
            predictions.append("Neutral")
            confidences.append(prob_dict.get("Neutral", max(prob)))

    df = pd.DataFrame({
        "message": messages,
        "sentiment": predictions,
        "confidence": [round(c, 2) for c in confidences]
    })

    return df


# -------- RUN ANALYSIS --------
result = analyze_whatsapp_chat("user_chat.txt")

counts = result["sentiment"].value_counts()
total = len(result)

print("\n--- CHAT SENTIMENT SUMMARY ---")
for sentiment, count in counts.items():
    percent = (count / total) * 100
    print(f"{sentiment}: {count} messages ({percent:.2f}%)")

overall_mood = counts.idxmax()
print("\nOverall Chat Mood:", overall_mood)

result.to_csv("chat_analysis_result.csv", index=False)
print("\n✅ Detailed analysis saved to chat_analysis_result.csv")
