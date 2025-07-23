import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load cleaned CSV
df = pd.read_csv("data/clean_questions.csv")

# Combine title + body into one column for better matching
df["full_text"] = df["title"].fillna('') + " " + df["body"].fillna('')

# Get user question
query = input("🔍 Ask your programming question: ")

# Step 1: Vectorize using TF-IDF
vectorizer = TfidfVectorizer(stop_words="english")
vectors = vectorizer.fit_transform([query] + df["full_text"].tolist())

# Step 2: Calculate cosine similarity
cos_sim = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

# Step 3: Find best match
top_idx = cos_sim.argmax()
top_score = cos_sim[top_idx]

# Step 4: Show result
print("\n✅ Best Matching Question:\n")
print("Title:", df.iloc[top_idx]["title"])
print("Tags:", df.iloc[top_idx]["tags"])
print("Score:", df.iloc[top_idx]["score"])
print("Link:", df.iloc[top_idx]["link"])
print("\nPreview:\n", df.iloc[top_idx]["body"][:500], "...")
