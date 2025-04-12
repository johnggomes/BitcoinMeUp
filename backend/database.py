import sqlite3
import csv
import os

DB_NAME = "bitcoin_me_up.db"
print("✅ Using database at:", os.path.abspath(DB_NAME))

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # So we can return dict-like rows
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Create content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                text_content TEXT,
                video_link TEXT,
                next_content_id INTEGER
            )
        ''')

        # Create onboarding_questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS onboarding_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                expected_keywords TEXT,
                weight_to_theme INTEGER
            )
        ''')

        # Create feedback_questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                related_content_id INTEGER,
                expected_keywords TEXT,
                FOREIGN KEY(related_content_id) REFERENCES content_table(id)
            )
        ''')
        # Create user_progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                completed_content_ids TEXT, -- comma-separated list of content IDs
                onboarding_answers TEXT,    -- JSON string of question_id:answer
                feedback_answers TEXT       -- JSON string of content_id: {question_id: answer}
            )
        ''')
        
        conn.commit()


def populate_content_table_from_csv(csv_file):
    with get_connection() as conn:
        cursor = conn.cursor()

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Skip empty rows and header rows (if needed)
            for row in reader:
                print(row) #Debug print

                title = row.get('title')
                title_description = row.get('title_description')
                title_link = row.get('title_link')

                if title and title_description and title_link:
                    cursor.execute('''
                        INSERT INTO content_table (title, text_content, video_link)
                        VALUES (?, ?, ?)
                    ''', (title.strip(), title_description.strip(), title_link.strip()))

        conn.commit()
        print("✅ Data successfully inserted into content_table.")

def populate_onboarding_questions_from_csv(csv_file):
    with get_connection() as conn:
        cursor = conn.cursor()

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            count = 0

            for row in reader:
                row = {k.strip(): v for k, v in row.items()}  # Clean keys

                question_text = row.get('question_text')
                expected_keywords = row.get('expected_keywords')
                weight_to_theme = row.get('weight_to_theme')

                if question_text and expected_keywords and weight_to_theme:
                    cursor.execute('''
                        INSERT INTO onboarding_questions (question_text, expected_keywords, weight_to_theme)
                        VALUES (?, ?, ?)
                    ''', (question_text.strip(), expected_keywords.strip(), weight_to_theme.strip()))
                    count += 1

        conn.commit()
        print(f"✅ Data successfully inserted into onboarding_questions. Rows inserted: {count}")

def populate_feedback_questions_from_csv(csv_file):
    with get_connection() as conn:
        cursor = conn.cursor()

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            count = 0

            for row in reader:
                row = {k.strip(): v for k, v in row.items()}  # Clean keys

                question_text = row.get('question_text')
                related_content_id = row.get('related_content_id')
                expected_keywords = row.get('expected_keywords')

                if question_text and expected_keywords:
                    cursor.execute('''
                        INSERT INTO feedback_questions (question_text, related_content_id, expected_keywords)
                        VALUES (?, ?, ?)
                    ''', (
                        question_text.strip(),
                        related_content_id.strip() if related_content_id else None,
                        expected_keywords.strip()
                    ))
                    count += 1

        conn.commit()
        print(f"✅ Data successfully inserted into feedback_questions. Rows inserted: {count}")

