import pandas as pd
from stackapi import StackAPI
import time

SITE = StackAPI('stackoverflow')

# Load the questions with accepted answer IDs
questions_df = pd.read_csv("data/stack_overflow_1000_questions.csv")

# Create answer column
questions_df["answer"] = ""

for idx, row in questions_df.iterrows():
    answer_id = row["accepted_answer_id"]
    try:
        answer = SITE.fetch('answers/{ids}', ids=[int(answer_id)], filter='withbody')
        if answer and 'items' in answer and len(answer['items']) > 0:
            body = answer['items'][0]['body_markdown']
            questions_df.at[idx, 'answer'] = body
        else:
            questions_df.at[idx, 'answer'] = "No answer found"
    except Exception as e:
        print(f"Error at index {idx}: {e}")
        questions_df.at[idx, 'answer'] = "Fetch failed"
    time.sleep(0.5)  # to respect rate limit

# Save final CSV
questions_df.to_csv("data/clean_questions_with_answers.csv", index=False)
print("✅ Answers saved to data/clean_questions_with_answers.csv")
