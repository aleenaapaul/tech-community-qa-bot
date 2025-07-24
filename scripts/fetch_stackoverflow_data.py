import requests
import time
import csv

# --- CONFIG ---
SITE = "stackoverflow"
TAGS = ["python"]  # Change/add more tags if needed
PAGES = 25  # Max allowed without API key (25 × 20 = 500 questions)
OUTPUT_FILE = "data/stack_overflow_1000_questions.csv"

# --- FETCH FUNCTION ---
def fetch_questions():
    all_data = []
    for page in range(1, PAGES + 1):
        print(f"Fetching page {page}...")
        url = f"https://api.stackexchange.com/2.3/questions?page={page}&pagesize=20&order=desc&sort=votes&tagged={'%3B'.join(TAGS)}&site={SITE}&filter=!)rTkraJr7YdK)3sFV87H"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"Error {res.status_code}: {res.text}")
            break

        items = res.json().get("items", [])
        for item in items:
            if not item.get("is_answered") or "accepted_answer_id" not in item:
                continue
            all_data.append({
                "question_id": item["question_id"],
                "title": item["title"],
                "link": item["link"],
                "score": item["score"],
                "tags": ";".join(item.get("tags", [])),
                "accepted_answer_id": item["accepted_answer_id"]
            })
        time.sleep(1)  # Be nice to API
    return all_data

# --- FETCH ACCEPTED ANSWERS ---
def fetch_accepted_answers(qdata):
    print("Fetching accepted answers...")
    for q in qdata:
        aid = q["accepted_answer_id"]
        url = f"https://api.stackexchange.com/2.3/answers/{aid}?order=desc&sort=activity&site={SITE}&filter=withbody"
        res = requests.get(url)
        if res.status_code != 200:
            print(f"Answer fetch failed: {aid}")
            q["answer"] = ""
        else:
            items = res.json().get("items", [])
            q["answer"] = items[0].get("body", "") if items else ""
        time.sleep(0.5)

# --- SAVE TO CSV ---
def save_to_csv(qdata):
    keys = ["title", "link", "score", "tags", "answer"]
    with open(OUTPUT_FILE, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for q in qdata:
            row = {k: q[k] for k in keys}
            writer.writerow(row)
    print(f"✅ Saved to {OUTPUT_FILE}")

# --- MAIN ---
if __name__ == "__main__":
    questions = fetch_questions()
    fetch_accepted_answers(questions)
    save_to_csv(questions)
