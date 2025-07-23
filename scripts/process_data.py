import json
import pandas as pd
from bs4 import BeautifulSoup  
# ✅ This must be at the top

questions = []

# Load the data from the JSON file
with open("data/questions_with_answers.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract and clean each question
for item in data["items"]:
    raw_answer = item.get("top_answer", "")
    clean_answer = BeautifulSoup(raw_answer, "html.parser").get_text()

    question = {
        "question_id": item.get("question_id"),
        "title": item.get("title"),
        "body": item.get("body"),
        "tags": ", ".join(item.get("tags", [])),
        "score": item.get("score"),
        "link": item.get("link"),
        "top_answer": clean_answer if clean_answer.strip() else "No answer available."
    }

    questions.append(question)

# Convert to DataFrame
df = pd.DataFrame(questions)

# Save to CSV
df.to_csv("data/clean_questions_with_answers.csv", index=False, encoding="utf-8")

print("✅ Cleaned questions + answers saved to clean_questions_with_answers.csv")


