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