import { useState, useEffect } from "react";

function ContentPage() {
  const [content, setContent] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);

  async function fetchNextContent() {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/next-content?user_id=user_123"
      );
      if (!response.ok) {
        throw new Error("Failed to fetch next content");
      }
      const data = await response.json();
      if (data.next_content) {
        setContent(data.next_content);
        setShowFeedback(false);
        setFeedback("");
      } else {
        setContent({
          title: "🎉 You've completed your learning path!",
          description: "",
          link: "",
        });
      }
    } catch (error) {
      console.error("Error fetching next content:", error);
    }
  }

  useEffect(() => {
    fetchNextContent();
  }, []);

  const handleMarkCompleted = async () => {
    if (!content || !content.content_id) return;

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/mark-content-completed",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: "user_123",
            content_id: content.content_id,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to mark content as completed");
      }

      console.log("✅ Content marked as completed!");
      setShowFeedback(true); // Show feedback form after marking completed
    } catch (error) {
      console.error("Error marking content completed:", error);
    }
  };

  const handleFeedbackSubmit = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/submit-feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: "user_123",
          content_id: content.content_id,
          answers: {
            1: feedback, // assuming only one feedback question ID 1 for now
          },
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to submit feedback");
      }

      console.log("✅ Feedback submitted!");
      await fetchNextContent(); // Load next content after submitting feedback
    } catch (error) {
      console.error("Error submitting feedback:", error);
    }
  };

  if (!content) {
    return <div>Loading content...</div>;
  }

  return (
    <div>
      <h2>{content.title}</h2>
      <p>{content.description}</p>
      {content.link && (
        <a href={content.link} target="_blank" rel="noopener noreferrer">
          View Resource
        </a>
      )}

      {content.title !== "🎉 You've completed your learning path!" &&
        !showFeedback && (
          <div>
            <button onClick={handleMarkCompleted} style={{ marginTop: "20px" }}>
              Mark as Completed
            </button>
          </div>
        )}

      {showFeedback && (
        <div style={{ marginTop: "20px" }}>
          <h3>Give us your feedback!</h3>
          <textarea
            rows="4"
            cols="50"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="What did you think of this content?"
          />
          <br />
          <button onClick={handleFeedbackSubmit} style={{ marginTop: "10px" }}>
            Submit Feedback
          </button>
        </div>
      )}
    </div>
  );
}

export default ContentPage;
