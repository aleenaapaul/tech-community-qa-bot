import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Load the cleaned question dataset
df = pd.read_csv("data/clean_questions.csv")  # adjust path if needed

# Load a lightweight semantic embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert all questions to embeddings
print("🔄 Encoding questions...")
question_embeddings = model.encode(df['title'].tolist(), convert_to_tensor=True)

# Get user input
user_input = input("\n🔍 Ask your programming question: ")
user_embedding = model.encode(user_input, convert_to_tensor=True)

# Calculate similarity
cos_scores = util.pytorch_cos_sim(user_embedding, question_embeddings)[0]
top_result = cos_scores.argmax().item()

# Show best match
best = df.iloc[top_result]
print("\n✅ Best Semantic Match:")
print(f"Title: {best['title']}")
print(f"Score: {best['score']}")
print(f"Link: {best['link']}")
