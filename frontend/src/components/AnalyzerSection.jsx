import { useState } from "react";
import axios from "axios";
import SentimentBarChart from "./SentimentBarChart";

import positiveSvg from "../assets/positive.svg";
import neutralSvg from "../assets/neutral.svg";
import negativeSvg from "../assets/negative.svg";
import HealthScoreChart from "./HealthScoreChart";


export default function AnalyzerSection() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(""); // ✅ NEW

  const API_URL = "https://whatsapp-sentiment-analysis-2.onrender.com/analyze";
  const analyzeChat = async () => {
    if (!file) {
      setErrorMsg("Please upload a WhatsApp .txt file");
      return;
    }

    setErrorMsg("");          // ✅ clear old errors
    setResult(null);          // ✅ reset old result

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const response = await axios.post(API_URL, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      // ✅ HANDLE BACKEND ERROR RESPONSE
      if (response.data?.error) {
        setErrorMsg(response.data.error);
        setLoading(false);
        return;
      }

      setResult(response.data);

    } catch (err) {
      console.error(err);
      setErrorMsg("Unable to analyze chat. Please try again.");
    }

    setLoading(false);
  };

  return (
    <section className="analyzer-section">
      <h2>Analyze Your WhatsApp Chat</h2>

      <div className="upload-box">
      <input
  id="fileUpload"
  type="file"
  accept=".txt"
  hidden
  onChange={(e) => setFile(e.target.files[0])}
/>

<label htmlFor="fileUpload" className="upload-card">
  <div className="upload-content">
    <div className="upload-icon">📄</div>

    <div className="upload-text">
      <p className="upload-title">
        {file ? file.name : "Upload WhatsApp Chat (.txt)"}
      </p>
      <p className="upload-sub">
        Export chat without media
      </p>
    </div>
  </div>
</label>

        <button onClick={analyzeChat}>
          {loading ? "Analyzing..." : "Analyze Chat"}
        </button>
      </div>

      {/* ✅ ERROR MESSAGE (NO CRASH) */}
      {errorMsg && <p className="error-text">{errorMsg}</p>}

      {/* ✅ RENDER RESULTS ONLY IF VALID */}
      {result && result.sentiment_counts && (
        <>
       <div className="mood-meter-section">
  <h3 className="meter-title">Overall Chat Mood</h3>

  <div className="mood-meter">
    <div className="meter-track">
      <div className="meter-segment negative">Negative</div>
      <div className="meter-segment neutral">Neutral</div>
      <div className="meter-segment positive">Positive</div>
    </div>

    {/* 🔻 PROFESSIONAL POINTER */}
    <div className={`meter-pointer ${result.overall_mood.toLowerCase()}`}>
      <div className="pointer-arrow"></div>

      <div className="pointer-label">
        <img
          src={
            result.overall_mood === "Positive"
              ? positiveSvg
              : result.overall_mood === "Negative"
              ? negativeSvg
              : neutralSvg
          }
          alt="mood"
        />
        <span>{result.overall_mood}</span>
      </div>
    </div>
  </div>
</div>


{result.health_score !== undefined && (
  <div className="health-section">
    <h3>Chat Health Score</h3>
    <HealthScoreChart score={result.health_score} />
  </div>
)}



<div className="sentiment-cards">
  <div className="sentiment-card">
    <img src={positiveSvg} alt="positive" />
    <h4>Positive</h4>
    <p className="percent">
      {result.sentiment_percentages?.Positive ?? 0}%
    </p>
  </div>

  <div className="sentiment-card">
    <img src={neutralSvg} alt="neutral" />
    <h4>Neutral</h4>
    <p className="percent">
      {result.sentiment_percentages?.Neutral ?? 0}%
    </p>
  </div>

  <div className="sentiment-card">
    <img src={negativeSvg} alt="negative" />
    <h4>Negative</h4>
    <p className="percent">
      {result.sentiment_percentages?.Negative ?? 0}%
    </p>
  </div>
</div>


          <SentimentBarChart counts={result.sentiment_counts} />
          {/* 🔴 TOP 3 NEGATIVE MESSAGES */}
{result.top_negative_messages &&
  result.top_negative_messages.length > 0 && (
    <div className="negative-section">
      <h3 className="negative-title">Most Negative Messages</h3>

      <ul className="negative-list">
        {result.top_negative_messages.map((msg, index) => (
          <li key={index} className="negative-item">
            “{msg.message}”
          </li>
        ))}
      </ul>
    </div>
  )}

          
        </>
        
      )}
    </section>
    
  );
}
