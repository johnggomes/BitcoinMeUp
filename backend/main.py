from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict
from database import (
    init_db,
    get_connection,
    populate_content_table_from_csv,
    populate_onboarding_questions_from_csv,
    populate_feedback_questions_from_csv
)
app = FastAPI()

# Initialize DB on start
init_db()

# Populate content table from CSV. Comment out after first run.

#populate_content_table_from_csv('content_table.csv')    
#populate_onboarding_questions_from_csv('onboarding_questions.csv')
#populate_feedback_questions_from_csv('feedback_questions.csv')

# Simple data model for onboarding response
class OnboardingResponse(BaseModel):
    user_id: str
    answers: Dict[str, str]  # question_id: answer

# New Pydantic model for mark completed request data
class MarkContentCompletedRequest(BaseModel):
    user_id: str
    content_id: int

class FeedbackResponse(BaseModel):
    user_id: str
    content_id: int
    answers: Dict[str, str]  # question_id: answer


@app.get("/")
def read_root():
    return {"message": "Hello, Bitcoiner or Bitcoin enthusiast!"}


@app.get("/onboarding-questions")
def get_onboarding_questions():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, question_text FROM onboarding_questions')
        questions = cursor.fetchall()

        # Convert Row objects to dict
        result = [{"id": row["id"], "question_text": row["question_text"]} for row in questions]

    return JSONResponse(content=result)

@app.post("/onboarding-answers")
def save_onboarding_answers(response: OnboardingResponse):
    import json
    from collections import Counter

    print("🟢 Onboarding answers endpoint hit")

    # Step 1: Save onboarding answers
    with get_connection() as conn:
        cursor = conn.cursor()

        answers_json = json.dumps(response.answers)

        cursor.execute('''
            INSERT INTO user_progress (user_id, onboarding_answers)
            VALUES (?, ?)
        ''', (response.user_id, answers_json))
        conn.commit()

        # Step 2: Fetch onboarding questions and build theme score
        cursor.execute('SELECT id, expected_keywords, weight_to_theme FROM onboarding_questions')
        questions = cursor.fetchall()

        theme_counter = Counter()

        for question in questions:
            q_id_str = str(question["id"])
            expected_keywords = [kw.strip().lower() for kw in question["expected_keywords"].split(",")]
            weight = question["weight_to_theme"]

            user_answer = response.answers.get(q_id_str, "").lower()

            print(f"QID: {q_id_str}, Expected: {expected_keywords}, User Answer: '{user_answer}'")

            # If user answer matches expected keywords, add weight to theme
            if any(keyword in user_answer for keyword in expected_keywords):
                theme_counter[weight] += 1

        if not theme_counter:
            return {"message": "No matching theme found from onboarding answers."}
        
        print("Theme Counter:", theme_counter)

        # Step 3: Select top theme
        top_theme = theme_counter.most_common(1)[0][0]

        # Step 4: Fetch related content (for now: first matching content)
        cursor.execute('''
            SELECT id, title, text_content, video_link FROM content_table
            WHERE id = ?
        ''', (top_theme,))

        content = cursor.fetchone()

        if not content:
            return {"message": "No content found for the selected theme."}

        content_response = {
            "content_id": content["id"],
            "title": content["title"],
            "description": content["text_content"],
            "link": content["video_link"]
        }

        return {
            "message": "Onboarding answers saved and first content selected.",
            "content": content_response
        }
    
@app.get("/progress-tree")
def get_progress_tree():
    user_id = "user_123"  # Replace with actual user ID from request context
    with get_connection() as conn:
        cursor = conn.cursor()

        # Fetch user progress
        cursor.execute('SELECT completed_content_ids FROM user_progress WHERE user_id = ?', (user_id,))
        user_progress = cursor.fetchone()

        if user_progress and user_progress["completed_content_ids"]:
            completed_ids = [int(cid) for cid in user_progress["completed_content_ids"].split(",") if cid.strip().isdigit()]
        else:
            completed_ids = []


        # Format data for frontend
        cursor.execute('SELECT id, title, next_content_id FROM content_table')
        content_items = cursor.fetchall()
        
        progress_tree = [
            {
                "content_id": row["id"],
                "title": row["title"],
                "next_content_id": row["next_content_id"],  # Could be None (end of branch)
                "status": "completed" if row["id"] in completed_ids else "pending"
            }
            for row in content_items
        ]

    return {"progress_tree": progress_tree}


# New POST endpoint to handle marking content as completed
@app.post("/mark-content-completed")
def mark_content_completed(request: MarkContentCompletedRequest):
    import json

    with get_connection() as conn:
        cursor = conn.cursor()

        # Fetch current completed content IDs
        cursor.execute('SELECT completed_content_ids FROM user_progress WHERE user_id = ?', (request.user_id,))
        user_progress = cursor.fetchone()

        if user_progress and user_progress["completed_content_ids"]:
            completed_ids = [int(cid) for cid in user_progress["completed_content_ids"].split(",") if cid.strip().isdigit()]
        else:
            completed_ids = []

        # Avoid duplication
        if request.content_id not in completed_ids:
            completed_ids.append(request.content_id)

            # Update the user_progress table
            completed_ids_str = ",".join(map(str, completed_ids))
            cursor.execute('''
                UPDATE user_progress
                SET completed_content_ids = ?
                WHERE user_id = ?
            ''', (completed_ids_str, request.user_id))
            conn.commit()

        print(f"✅ User '{request.user_id}' marked content ID {request.content_id} as completed. Updated list: {completed_ids}")
        
        return {"message": "Content marked as completed."}

@app.get("/feedback-questions")
def get_feedback_questions(content_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, question_text FROM feedback_questions
            WHERE related_content_id = ?
            OR related_content_id IS NULL
        ''', (content_id,))

        questions = cursor.fetchall()

        result = [{"id": row["id"], "question_text": row["question_text"]} for row in questions]

    return {"feedback_questions": result}

@app.post("/submit-feedback")
def submit_feedback(response: FeedbackResponse):
    import json

    with get_connection() as conn:
        cursor = conn.cursor()

        # Fetch existing feedback
        cursor.execute('SELECT feedback_answers FROM user_progress WHERE user_id = ?', (response.user_id,))
        user_progress = cursor.fetchone()

        if user_progress and user_progress["feedback_answers"]:
            feedback_data = json.loads(user_progress["feedback_answers"])
        else:
            feedback_data = {}

        # Update feedback for this content
        feedback_data[str(response.content_id)] = response.answers

        # Save back to database
        feedback_json = json.dumps(feedback_data)
        cursor.execute('''
            UPDATE user_progress
            SET feedback_answers = ?
            WHERE user_id = ?
        ''', (feedback_json, response.user_id))
        conn.commit()

    return {"message": "Feedback submitted successfully."}


@app.get("/next-content")
def get_next_content(user_id: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        # Fetch user progress
        cursor.execute('SELECT completed_content_ids FROM user_progress WHERE user_id = ?', (user_id,))
        user_progress = cursor.fetchone()

        if not user_progress or not user_progress["completed_content_ids"]:
            return {"message": "No completed content found. Start your journey!"}

        # Get list of completed IDs
        completed_ids = [int(cid) for cid in user_progress["completed_content_ids"].split(",") if cid.strip().isdigit()]
        last_completed_id = completed_ids[-1]  # Get the last completed content

        # Fetch the next content ID
        cursor.execute('SELECT next_content_id FROM content_table WHERE id = ?', (last_completed_id,))
        next_content = cursor.fetchone()

        if not next_content or not next_content["next_content_id"]:
            return {"message": "You've completed the learning path!"}

        # Fetch the next content details
        cursor.execute('SELECT id, title, text_content, video_link FROM content_table WHERE id = ?', (next_content["next_content_id"],))
        content = cursor.fetchone()

        if not content:
            return {"message": "Next content not found in database."}

        content_response = {
            "content_id": content["id"],
            "title": content["title"],
            "description": content["text_content"],
            "link": content["video_link"]
        }

        return {"next_content": content_response}