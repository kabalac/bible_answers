import { useState } from "react";
import "./App.css";

// const API_URL = "http://127.0.0.1:8000";

const API_URL = "";

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [feeling, setFeeling] = useState("");
  const [response, setResponse] = useState("");
  const [scripture, setScripture] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isResetting, setIsResetting] = useState(false);

  const findAnswer = async () => {
    if (!feeling.trim()) {
      setError("Please tell us how you're feeling.");
      return;
    }

    setLoading(true);
    setResponse("");
    setScripture(null);
    setError("");

    try {
      const apiResponse = await fetch(`${API_URL}/answer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          feeling: feeling.trim(),
        }),
      });

      if (!apiResponse.ok) {
        throw new Error("Unable to get an answer.");
      }

      const data = await apiResponse.json();

      setResponse(data.response);
      setScripture(data.scripture);
    } catch (error) {
      console.error(error);

      setError(
        "Something went wrong. Please make sure the Bible Answers server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      findAnswer();
    }
  };

  const beginAgain = () => {
    setIsResetting(true);

    setTimeout(() => {
      setFeeling("");
      setResponse("");
      setScripture(null);
      setError("");
      setIsResetting(false);
    }, 700);
  };

  return (
    <main className={`landing-page ${darkMode ? "dark-mode" : ""}`}>
      <section className={`hero ${isResetting ? "resetting" : ""}`}>
        <div className="top-controls">

          <button
            className="donate-button"
            onClick={() => {
              alert("Please donate ₹1 to your nearby church.");
            }}
            title="Donate ₹1 to your nearby church"
          >
            Donate
          </button>

          <button
            className={`theme-toggle ${darkMode ? "dark" : ""}`}
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle dark mode"
          >
            <span className="theme-icon">☀</span>

            <span className="toggle-track">
              <span className="toggle-thumb"></span>
            </span>

            <span className="theme-icon">☾</span>
          </button>

        </div>
        {/* Brand */}
        <div className="cross">✝</div>

        <p className="brand">BIBLE ANSWERS</p>

        {/* Hero */}
        <h1>
          What is on
          <br />
          your heart today?
        </h1>

        <p className="subtitle">
          Share how you feel. Find comfort and guidance
          <br />
          through the words of the Bible.
        </p>

        {/* Input */}
        <div className="answer-box">

          <div className="textarea-wrapper">
            <textarea
              placeholder="Tell us what's on your heart… e.g., I feel anxious about my future." rows="4"
              value={feeling}
              maxLength={500}
              onChange={(event) => {
                setFeeling(event.target.value);
                setError("");
              }}
              onKeyDown={handleKeyDown}
              disabled={loading || !!response}
            />

            <div className="character-count">
              {feeling.length} / 500
            </div>
          </div>

          {!response && (
            <button
              className="find-button"
              onClick={findAnswer}
              disabled={loading}
            >
              {loading ? "Finding..." : "Find an Answer"}
            </button>
          )}
        </div>

        {/* Error */}
        {error && <p className="error">{error}</p>}

        {/* Response */}
        {response && (
          <div className={`response ${isResetting ? "resetting" : ""}`}>

            <div className="response-icon">✦</div>

            <p className="response-text">
              {response}
            </p>

            {scripture && (
              <div className="scripture">

                <p className="scripture-text">
                  "{scripture.text}"
                </p>

                <span className="scripture-reference">
                  — {scripture.book} {scripture.chapter}:{scripture.verse}
                </span>

              </div>
            )}

            <button
              className="begin-again"
              onClick={beginAgain}
            >
              Begin again
            </button>

          </div>
        )}

        {/* Footer Verse */}
        <div className={`verse ${isResetting ? "resetting" : ""}`}>
          <p>
            "Your word is a lamp for my feet, a light on my path."
          </p>

          <span>
            — Psalm 119:105
          </span>
        </div>

      </section>
    </main>
  );
}

export default App;