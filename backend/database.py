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

        # Create question table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                expected_answer_keywords TEXT,
                content_id INTEGER,
                FOREIGN KEY(content_id) REFERENCES content_table(id)
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