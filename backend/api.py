import re
import pickle
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

nltk.download("stopwords")

# LOAD MODEL
model = pickle.load(open("sentiment_logistic.pkl", "rb"))
vectorizer = pickle.load(open("tfidf_logistic.pkl", "rb"))

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

app = FastAPI(title="WhatsApp Sentiment Analysis API")

# CORS (for frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CLEAN TEXT
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return " ".join(words)

def extract_whatsapp_messages(lines):
    messages = []

    pattern = re.compile(
        r"^\[.*?\]\s.*?:\s(.*)$"
    )

    for line in lines:
        # skip encryption/system lines
        if "end-to-end encrypted" in line.lower():
            continue

        match = pattern.match(line)
        if match:
            msg = match.group(1).strip()
            if msg and "<Media omitted>" not in msg:
                messages.append(msg)

    return messages

@app.get("/")
def home():
    return {"message": "WhatsApp Sentiment Analysis API is running"}

@app.post("/analyze")
async def analyze_chat(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    lines = text.splitlines()

    messages = extract_whatsapp_messages(lines)
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
            "confidence": round(prob_dict[sentiment], 2)
        })

        # ✅ TOTAL MESSAGES
    total = sum(counts.values())

    # ✅ SENTIMENT PERCENTAGES
    percentages = {
        "Positive": round((counts["Positive"] / total) * 100, 2) if total else 0,
        "Neutral": round((counts["Neutral"] / total) * 100, 2) if total else 0,
        "Negative": round((counts["Negative"] / total) * 100, 2) if total else 0
    }

    # ✅ CHAT HEALTH SCORE (0–100)
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

    # ✅ TOP 3 NEGATIVE MESSAGES (BY CONFIDENCE)
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

