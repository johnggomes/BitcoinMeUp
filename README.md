# BitcoinMeUp

What is the projet?
Build an AI-assisted learning platform that serves educational content dynamically based on user input, tracks progress visually (progress tree), and allows future scaling. It is meant to be a cross over of ChatGPT's and DuoLingo's UI

What does it do?
Serves the user a tailored step by step learning plan to understand Bitcoin

How to install it?
To be figured out

How to use it?
Simply lauch the webviewer in your browser and begin with the interview

Dependencies?
Install the requirements file

Optional stuff:

Appendix
    

+----------------------+
|     User Input       |
+----------+-----------+
           |
           v
+----------+-----------+
| Frontend (React)     |
| Chat UI + Tree UI    |
+----------+-----------+
           |
           v
+----------+-----------+
| Backend (FastAPI)    |
| OpenAI API | DB Logic|
+----------+-----------+
           |
           v
+----------+-----------+
| SQLite Database      |
| Content + Questions  |
+----------------------+


User
  |
  +-- OnboardingQuestionResponse
  |
  +-- ContentProgress
  |
  +-- FeedbackResponse
            |
            +-- feedback_questions
Content
  |
  +-- feedback_questions


____________________________________
[User lands on web app]
            |
            v
[Onboarding Flow: onboarding_questions.csv]
            |
            v
[AI interprets answers + recommends initial content]
            |
            v
[First content delivered (from content_table)]
            |
            v
[Post-content feedback: feedback_questions.csv]
            |
            v
[Answers recorded]
            |
            v
[AI uses onboarding + feedback to recommend next content]
            |
            v
[Progress tree updates, repeat cycle]