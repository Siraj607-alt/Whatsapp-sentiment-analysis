import chatSvg from "../assets/chat.svg";
import aiSvg from "../assets/ai.svg";
import insightSvg from "../assets/insight.svg";
import privacySvg from "../assets/privacy.svg";

export default function AboutSection() {
  return (
    <section className="about-section">
      <div className="about-content">
        <h1>WhatsApp Chat Sentiment Analysis</h1>
        <p className="subtitle">
          An AI-powered system that understands emotions in WhatsApp conversations
          using Machine Learning and Natural Language Processing.
        </p>

        <div className="about-features">

  {/* 1️⃣ INPUT */}
  <div className="feature-card">
    <img src={chatSvg} alt="chat analysis" />
    <h3>Real WhatsApp Data</h3>
    <p>
      Analyzes exported WhatsApp chats without modifying the original
      conversation structure.
    </p>
  </div>

  {/* 2️⃣ PROCESS */}
  <div className="feature-card">
    <img src={aiSvg} alt="ai model" />
    <h3>ML-Powered Model</h3>
    <p>
      Built using Logistic Regression with TF-IDF n-grams for high accuracy
      on short conversational texts.
    </p>
  </div>

  {/* 3️⃣ OUTPUT / VALUE */}
  <div className="feature-card">
    <img src={insightSvg} alt="actionable insights" />
    <h3>Actionable Insights</h3>
    <p>
      Highlights negative patterns, emotional trends, and critical messages
      to understand conversation health.
    </p>
  </div>

  {/* 4️⃣ TRUST */}
  <div className="feature-card">
    <img src={privacySvg} alt="privacy focused" />
    <h3>Privacy-Focused Analysis</h3>
    <p>
      Chats are processed securely without storing personal data, ensuring
      complete privacy and user control.
    </p>
  </div>

</div>

      </div>
    </section>
  );
}
