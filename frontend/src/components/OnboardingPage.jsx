import { useState, useEffect } from "react";
import { fetchOnboardingQuestions } from "../api/backend";

function OnboardingPage({ onComplete }) {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});

  useEffect(() => {
    async function loadQuestions() {
      try {
        const data = await fetchOnboardingQuestions();
        setQuestions(data);
      } catch (error) {
        console.error("Error loading questions:", error);
      }
    }
    loadQuestions();
  }, []);

  const handleChange = (e, questionId) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: e.target.value,
    }));
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        user_id: "user_123", // For now, static user ID
        answers: answers,
      };

      const response = await fetch("http://127.0.0.1:8000/onboarding-answers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to submit onboarding answers");
      }

      console.log("✅ Onboarding answers submitted!");
      onComplete(); // move to ContentPage
    } catch (error) {
      console.error("Submission error:", error);
    }
  };

  return (
    <div>
      <h2>Onboarding Questions</h2>
      {questions.map((q) => (
        <div key={q.id}>
          <label>{q.question_text}</label>
          <br />
          <small style={{ color: "gray" }}>
            Suggested: {q.expected_keywords}
          </small>
          <br />
          <input
            type="text"
            value={answers[q.id] || ""}
            onChange={(e) => handleChange(e, q.id)}
          />
          <br />
          <br />
        </div>
      ))}

      <button onClick={handleSubmit}>Submit Answers</button>
    </div>
  );
}

export default OnboardingPage;
