import re
import pandas as pd
import nltk
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download stopwords (only first time)
nltk.download("stopwords")

# ---------- STEP 1: READ FILE ----------
file_path = "WhatsApp Chat with Kaggle_Community Discussions 2.txt"

with open(file_path, encoding="utf-8") as f:
    lines = f.readlines()

print("File loaded successfully")
print("Total lines:", len(lines))


# ---------- STEP 2: EXTRACT REAL MESSAGES ----------
messages = []

pattern = r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}.*?-.*?:\s(.*)"

for line in lines:
    match = re.search(pattern, line)
    if match:
        msg = match.group(1).strip()
        if msg and "<Media omitted>" not in msg:
            messages.append(msg)

df = pd.DataFrame(messages, columns=["message"])
print("Total valid messages:", len(df))
print(df.head())


# ---------- STEP 3: AUTO-LABEL SENTIMENT ----------
def auto_label(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

df["sentiment"] = df["message"].apply(auto_label)
print(df["sentiment"].value_counts())


# ---------- STEP 4: CLEAN TEXT ----------
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return " ".join(words)

df["clean_message"] = df["message"].apply(clean_text)
print(df.head())


# ---------- STEP 5: SAVE FINAL DATASET ----------
df_final = df[["clean_message", "sentiment"]]
df_final.to_csv("whatsapp_sentiment_final.csv", index=False)

print("✅ Dataset saved as whatsapp_sentiment_final.csv")
