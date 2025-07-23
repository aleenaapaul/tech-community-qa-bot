import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

input_path = "data/clean_questions.csv"
output_path = "data/clean_questions_with_answers.csv"

df = pd.read_csv(input_path)
df["answer"] = ""

def fetch_top_answer(link):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com",
            "DNT": "1",
            "Connection": "keep-alive"
        }
        res = requests.get(link, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"⚠️ Failed to fetch: {link} [Status Code: {res.status_code}]")
            return None
        soup = BeautifulSoup(res.text, "html.parser")

        # Try accepted answer
        accepted = soup.select_one("div.accepted-answer .js-post-body")
        if accepted:
            return accepted.get_text(strip=True)

        # Fallback: top-voted
        top_answer = soup.select_one("div.answer .js-post-body")
        return top_answer.get_text(strip=True) if top_answer else None

    except Exception as e:
        print("Error:", e)
        return None

# Loop and scrape
for idx, row in df.iterrows():
    print(f"Fetching {idx + 1}/{len(df)}: {row['title']}")
    answer = fetch_top_answer(row['link'])
    df.at[idx, "answer"] = answer if answer else "No answer found."
    time.sleep(1)

    if idx % 10 == 0:
        df.to_csv(output_path, index=False)

df.to_csv(output_path, index=False)
print("✅ Done! Saved to", output_path)
