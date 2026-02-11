import re
import pickle
import pandas as pd
import unicodedata
import chardet

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

# ===============================
# APP SETUP
# ===============================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nltk.download("stopwords")

# ===============================
# LOAD MODEL
# ===============================
model = pickle.load(open("sentiment_logistic.pkl", "rb"))
vectorizer = pickle.load(open("tfidf_logistic.pkl", "rb"))

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

# ===============================
# TEXT CLEANING (TRAINING SAME)
# ===============================
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return " ".join(words)

# ===============================
# FILE READER (ANDROID + IOS)
# ===============================
def read_uploaded_file(upload_file: UploadFile):
    raw = upload_file.file.read()

    detected = chardet.detect(raw)
    encoding = detected.get("encoding") or "utf-8"

    try:
        text = raw.decode(encoding)
    except Exception:
        text = raw.decode("utf-8", errors="ignore")

    # Normalize Android unicode
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u202f", " ").replace("\u00a0", " ")

    return text.splitlines()

# ===============================
# UNIVERSAL WHATSAPP EXTRACTOR
# ===============================
import unicodedata

def extract_whatsapp_messages(lines):
    messages = []

    SYSTEM_PHRASES = (
        "messages and calls are end-to-end encrypted",
        "end-to-end encrypted",
        "is a contact",
        "you deleted this message",
    )

    # WhatsApp Android + iOS regex
    pattern = re.compile(
        r"^\[?.*?\]?\s?-?\s?.*?:\s(.*)$"
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue

        lower = line.lower()
        if any(p in lower for p in SYSTEM_PHRASES):
            continue

        match = pattern.match(line)

        if match:
            message = match.group(1).strip()

            # remove empty or junk messages
            if len(message) < 2:
                continue

            if "<media omitted>" in message.lower():
                continue

            messages.append(message)

    return messages


# ===============================
# API ENDPOINT
# ===============================
@app.post("/analyze")
async def analyze_chat(file: UploadFile = File(...)):
    lines = read_uploaded_file(file)

    messages = extract_whatsapp_messages(lines)

    # DEBUG (remove after confirmation)
    print("Extracted messages:", len(messages))

    if not messages:
        return {
            "error": "No valid WhatsApp messages found. Please upload a valid chat export."
        }

    clean_msgs = [clean_text(m) for m in messages]
    vectors = vectorizer.transform(clean_msgs)

    probs = model.predict_proba(vectors)
    classes = model.classes_

    results = []
    counts = {"Positive": 0, "Neutral": 0, "Negative": 0}

    for msg, prob in zip(messages, probs):
        prob_dict = dict(zip(classes, prob))

        if prob_dict.get("Negative", 0) >= 0.40:
            sentiment = "Negative"
        elif prob_dict.get("Positive", 0) >= 0.45:
            sentiment = "Positive"
        else:
            sentiment = "Neutral"

        counts[sentiment] += 1

        results.append({
            "message": msg,
            "sentiment": sentiment,
            "confidence": round(prob_dict.get(sentiment, max(prob)), 2)
        })

    total = sum(counts.values())

    percentages = {
        "Positive": round((counts["Positive"] / total) * 100, 2),
        "Neutral": round((counts["Neutral"] / total) * 100, 2),
        "Negative": round((counts["Negative"] / total) * 100, 2),
    }

    health_score = max(
        0,
        min(
            100,
            round(
                percentages["Positive"]
                + (percentages["Neutral"] * 0.5)
                - percentages["Negative"]
            )
        )
    )

    top_negative = sorted(
        [r for r in results if r["sentiment"] == "Negative"],
        key=lambda x: x["confidence"],
        reverse=True
    )[:3]

    return {
        "total_messages": total,
        "overall_mood": max(counts, key=counts.get),
        "sentiment_counts": counts,
        "sentiment_percentages": percentages,
        "health_score": health_score,
        "top_negative_messages": top_negative
    }
