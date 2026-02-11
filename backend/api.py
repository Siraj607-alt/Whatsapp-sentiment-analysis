import re
import pickle
import chardet
import unicodedata
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

# ===================================
# DOWNLOAD NLTK DATA (RENDER SAFE)
# ===================================
nltk.download("stopwords")

# ===================================
# LOAD MODEL
# ===================================
model = pickle.load(open("sentiment_logistic.pkl", "rb"))
vectorizer = pickle.load(open("tfidf_logistic.pkl", "rb"))

stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

app = FastAPI(title="WhatsApp Sentiment Analysis API")

# ===================================
# CORS
# ===================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================
# CLEAN TEXT
# ===================================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    words = text.split()
    words = [stemmer.stem(w) for w in words if w not in stop_words]
    return " ".join(words)

# ===================================
# FIXED WHATSAPP EXTRACTOR
# ===================================
def extract_whatsapp_messages(lines):
    messages = []

    SYSTEM_PHRASES = (
        "messages and calls are end-to-end encrypted",
        "end-to-end encrypted",
        "is a contact",
        "you deleted this message",
    )

    # ✅ Correct regex for WhatsApp format
    pattern = re.compile(r"^\[?.*?\]?\s?-?\s?.*?:\s(.*)$")

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

            if len(message) < 2:
                continue

            if "<media omitted>" in message.lower():
                continue

            messages.append(message)

    return messages

# ===================================
# HOME ROUTE
# ===================================
@app.get("/")
def home():
    return {"message": "WhatsApp Sentiment Analysis API is running"}

# ===================================
# ANALYZE CHAT
# ===================================
@app.post("/analyze")
async def analyze_chat(file: UploadFile = File(...)):
    raw = await file.read()

    # Detect encoding
    detected = chardet.detect(raw)
    encoding = detected.get("encoding") or "utf-8"

    try:
        text = raw.decode(encoding)
    except Exception:
        text = raw.decode("utf-8", errors="ignore")

    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u202f", " ").replace("\u00a0", " ")

    lines = text.splitlines()
    messages = extract_whatsapp_messages(lines)

    if not messages:
        return {
            "error": "No valid WhatsApp messages found. Please upload a valid chat export."
        }

    # Clean + Vectorize
    clean_msgs = [clean_text(m) for m in messages]
    vectors = vectorizer.transform(clean_msgs)

    probs = model.predict_proba(vectors)
    classes = model.classes_

    results = []
    counts = {"Positive": 0, "Neutral": 0, "Negative": 0}

    for msg, prob in zip(messages, probs):
        prob_dict = dict(zip(classes, prob))

        # DEBUG PRINTS (OPTIONAL)
        print("MESSAGE:", msg)
        print("PROBS:", prob_dict)
        print("--------------")

        positive_score = prob_dict.get("Positive", 0)
        neutral_score = prob_dict.get("Neutral", 0)

        # SMART POSITIVE BOOST
        if positive_score > neutral_score * 0.75:
            sentiment = "Positive"
        else:
            sentiment = classes[prob.argmax()]

        counts[sentiment] += 1

        results.append({
            "message": msg,
            "sentiment": sentiment,
            "confidence": round(prob_dict.get(sentiment, max(prob)), 2)
        })

    # ===================================
    # SUMMARY
    # ===================================
    total = sum(counts.values())

    percentages = {
        "Positive": round((counts["Positive"] / total) * 100, 2) if total else 0,
        "Neutral": round((counts["Neutral"] / total) * 100, 2) if total else 0,
        "Negative": round((counts["Negative"] / total) * 100, 2) if total else 0
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
