from fastapi import FastAPI
from database import init_db, populate_content_table_from_csv

app = FastAPI()

# Initialize DB on start
init_db()

# Populate content table from CSV
populate_content_table_from_csv('content_table.csv')

@app.get("/")
def read_root():
    return {"message": "Hello, Bitcoiner or Bitcoin enthusiast!"}