import requests
import csv

# -------------------------------
# Step 1: Fetch Questions from Stack Overflow API
# -------------------------------
def fetch_questions_from_api(tag="python", pages=2):
    base_url = "https://api.stackexchange.com/2.3/questions"
    questions = []

    for page in range(1, pages + 1):
        params = {
            "order": "desc",
            "sort": "votes",
            "tagged": tag,
            "site": "stackoverflow",
            "pagesize": 20,
            "page": page
        }

        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"API call failed: Page {page}, Status Code {response.status_code}")
            continue

        data = response.json()
        for item in data["items"]:
            questions.append({
                "title": item["title"],
                "link": item["link"],
                "score": item["score"]
            })

    return questions

# -------------------------------
# Step 2: Save Questions to CSV
# -------------------------------
def save_to_csv(data, filename="data/questions.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "link", "score"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# -------------------------------
# Main Program
# -------------------------------
if __name__ == "__main__":
    tag = "python"
    pages = 2

    print(f"📥 Fetching questions tagged '{tag}' from Stack Overflow...")
    questions = fetch_questions_from_api(tag, pages)

    if questions:
        save_to_csv(questions)
        print(f"✅ {len(questions)} questions saved to 'data/questions.csv'")
    else:
        print("⚠ No questions fetched.")
