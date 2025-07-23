import pandas as pd

# Read raw questions
df = pd.read_csv("data/questions.csv")

# Drop duplicates and missing entries
df.drop_duplicates(subset="title", inplace=True)
df.dropna(subset=["title", "link", "score"], inplace=True)

# Clean up spacing
df["title"] = df["title"].str.strip()

# Reset index
df.reset_index(drop=True, inplace=True)

# Save cleaned file
df.to_csv("data/clean_questions.csv", index=False)
print("✅ Cleaned questions saved to data/clean_questions.csv")
