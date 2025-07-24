import pandas as pd
from bs4 import BeautifulSoup

INPUT_FILE = "data/stack_overflow_1000_questions.csv"
OUTPUT_FILE = "data/clean_questions_with_answers.csv"

print("Cleaning HTML from answers...")

df = pd.read_csv(INPUT_FILE)

def clean_html(raw_html):
    if pd.isna(raw_html):
        return ""
    return BeautifulSoup(raw_html, "html.parser").get_text()

df["answer"] = df["answer"].apply(clean_html)
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Cleaned answers saved to {OUTPUT_FILE}")
