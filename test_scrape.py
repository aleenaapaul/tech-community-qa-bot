import requests
from bs4 import BeautifulSoup

def fetch_top_answer(link):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com",
            "DNT": "1",
            "Connection": "keep-alive"
        }
        res = requests.get(link, headers=headers)
        if res.status_code != 200:
            print(f"⚠️ Failed to fetch: {link} [Status Code: {res.status_code}]")
            return
        soup = BeautifulSoup(res.text, "html.parser")
        accepted = soup.select_one("div.accepted-answer .js-post-body") or \
                   soup.select_one("div.answercell .js-post-body")
        if accepted:
            print("✅ Answer Fetched:")
            print(accepted.get_text(strip=True))
        else:
            print("❌ No answer content found.")
    except Exception as e:
        print("⚠️ Exception:", e)

# Test
fetch_top_answer("https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do-in-python")
