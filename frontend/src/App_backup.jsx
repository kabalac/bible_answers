import { useEffect, useState } from "react";
import "./App.css";

// const API_URL = "http://127.0.0.1:8000";

const API_URL = "";

function App() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [darkMode, setDarkMode] = useState(false);
  const [feeling, setFeeling] = useState("");
  const [response, setResponse] = useState("");
  const [scripture, setScripture] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isResetting, setIsResetting] = useState(false);
  const [beginAgainCount, setBeginAgainCount] = useState(0);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackClosing, setFeedbackClosing] = useState(false);
  const getDeviceType = () => {
    const userAgent = navigator.userAgent.toLowerCase();

    if (/ipad|tablet/.test(userAgent)) {
      return "tablet";
    }

    if (/android|iphone|ipod|mobile/.test(userAgent)) {
      return "mobile";
    }

    return "desktop";
  };
  // ============================================================
  // ANALYTICS — SESSION START
  // ============================================================

  useEffect(() => {
    fetch(`${API_URL}/analytics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        event: "session_started",
        session_id: sessionId,
        device_type: getDeviceType(),
      }),
    }).catch((error) => {
      console.error("Analytics error:", error);
    });
  }, [sessionId]);

  // ============================================================
  // FIND ANSWER
  // ============================================================

  const findAnswer = async () => {
    if (!feeling.trim()) {
      setError("Please tell us how you're feeling.");
      return;
    }

    setLoading(true);
    setResponse("");
    setScripture(null);
    setError("");

    // Record when the answer request begins
    const requestStartTime = performance.now();

    // Analytics: answer requested
    fetch(`${API_URL}/analytics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        event: "answer_requested",
        session_id: sessionId,
      }),
    }).catch((error) => {
      console.error("Analytics error:", error);
    });

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

      // Calculate response time
      const responseTimeMs = Math.round(
        performance.now() - requestStartTime
      );

      // Analytics: answer completed
      fetch(`${API_URL}/analytics`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          event: "answer_completed",
          session_id: sessionId,
          response_time_ms: responseTimeMs,
          category: data.analytics?.category || null,
          scripture_reference: data.analytics?.scripture_reference || null,
        }),
      }).catch((error) => {
        console.error("Analytics error:", error);
      });
    } catch (error) {
      console.error(error);

      setError(
        "Something went wrong. Please make sure the Bible Answers server is running."
      );
    } finally {
      setLoading(false);
    }
  };
  // ============================================================
  // KEYBOARD HANDLER
  // ============================================================

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      findAnswer();
    }
  };

  // ============================================================
  // BEGIN AGAIN
  // ============================================================

  const beginAgain = () => {
    const nextCount = beginAgainCount + 1;

    setBeginAgainCount(nextCount);

    // Analytics: every Begin Again
    fetch(`${API_URL}/analytics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        event: "begin_again",
        session_id: sessionId,
      }),
    }).catch((error) => {
      console.error("Analytics error:", error);
    });

    // Analytics: third Begin Again reached
    if (nextCount === 3) {
      fetch(`${API_URL}/analytics`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          event: "feedback_prompt_shown",
          session_id: sessionId,
        }),
      }).catch((error) => {
        console.error("Analytics error:", error);
      });
    }

    setIsResetting(true);

    setTimeout(() => {
      setFeeling("");
      setResponse("");
      setScripture(null);
      setError("");
      setIsResetting(false);

      // Show feedback after the third Begin Again
      if (nextCount === 3) {
        setShowFeedback(true);
      }
    }, 700);
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <main className={`landing-page ${darkMode ? "dark-mode" : ""}`}>
      <section className={`hero ${isResetting ? "resetting" : ""}`}>
        <div className="top-controls">

          <button
            className="donate-button"
            onClick={() => {
              fetch(`${API_URL}/analytics`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  event: "donate_clicked",
                  session_id: sessionId,
                }),
              }).catch((error) => {
                console.error("Analytics error:", error);
              });

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
              placeholder="Tell us what's on your heart… e.g., I feel anxious about my future."
              rows="4"
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
        {/* Feedback */}

        {showFeedback && (
          <div className={`feedback-card ${feedbackClosing ? "feedback-closing" : ""}`}>
            <p className="feedback-title">
              How was your experience?
            </p>

            <p className="feedback-subtitle">
              Your feedback helps us make Bible Answers better.
            </p>

            <div className="feedback-options">
              <button
                onClick={() => {
                  console.log("Feedback: helpful");

                  fetch(`${API_URL}/analytics`, {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                      event: "feedback_submitted",
                      session_id: sessionId,
                      feedback: "helpful",
                    }),
                  }).catch((error) => {
                    console.error("Analytics error:", error);
                  });

                  setFeedbackClosing(true);

                  setTimeout(() => {
                    setShowFeedback(false);
                    setFeedbackClosing(false);
                  }, 350);
                }}
              >
                😊 Helpful
              </button>

              <button
                onClick={() => {
                  console.log("Feedback: okay");

                  fetch(`${API_URL}/analytics`, {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                      event: "feedback_submitted",
                      session_id: sessionId,
                      feedback: "okay",
                    }),
                  }).catch((error) => {
                    console.error("Analytics error:", error);
                  });

                  setFeedbackClosing(true);

                  setTimeout(() => {
                    setShowFeedback(false);
                    setFeedbackClosing(false);
                  }, 350);
                }}
              >
                😐 Okay
              </button>

              <button
                onClick={() => {
                  console.log("Feedback: not_helpful");

                  fetch(`${API_URL}/analytics`, {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                      event: "feedback_submitted",
                      session_id: sessionId,
                      feedback: "not_helpful",
                    }),
                  }).catch((error) => {
                    console.error("Analytics error:", error);
                  });

                  setFeedbackClosing(true);

                  setTimeout(() => {
                    setShowFeedback(false);
                    setFeedbackClosing(false);
                  }, 350);
                }}
              >
                🙁 Not helpful
              </button>
            </div>

            <button
              className="feedback-later"
              onClick={() => setShowFeedback(false)}
            >
              Maybe later
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