import { useState, useEffect } from "react";
import "./ProgressTreePage.css"; // We will also create this CSS file

function ProgressTreePage() {
  const [progress, setProgress] = useState([]);

  useEffect(() => {
    async function fetchProgress() {
      try {
        const response = await fetch("http://127.0.0.1:8000/progress-tree");
        if (!response.ok) {
          throw new Error("Failed to fetch progress tree");
        }
        const data = await response.json();
        setProgress(data);
      } catch (error) {
        console.error("Error fetching progress tree:", error);
      }
    }
    fetchProgress();
  }, []);

  return (
    <div>
      <h2>Your Learning Journey</h2>
      <div className="progress-tree-container">
        {progress.map((item) => (
          <div
            key={item.content_id}
            className={`progress-bubble ${
              item.status === "completed" ? "completed" : "pending"
            }`}
          >
            {item.title}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProgressTreePage;
