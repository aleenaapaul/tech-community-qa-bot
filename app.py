import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import torch

MAX_TOKENS = 1024  # BART input limit

def truncate_text(text, max_tokens=MAX_TOKENS):
    return " ".join(text.split()[:max_tokens])

# -----------------------------
# Load Summarization Models
# -----------------------------
@st.cache_resource
def load_summarizer(model_name):
    return pipeline("summarization", model=model_name)

# -----------------------------
# Sidebar Configuration
# -----------------------------
st.sidebar.title("⚙️ Configuration")

view_mode = st.sidebar.radio("Select View Mode", ["Ask Question", "Browse Dataset"])
selected_tag = st.sidebar.selectbox("Filter Questions by Tag", ["python", "javascript", "flask", "django", "c++", "java"])
num_results = st.sidebar.slider("Top N Matches to Compare", 3, 20, 10)
summary_threshold = st.sidebar.slider("Minimum Words Before Summarizing", 60, 300, 80)

st.sidebar.markdown("---")
st.sidebar.markdown("Model: `all-MiniLM-L6-v2`")

llm_choice = st.sidebar.selectbox("Choose LLM for Summarization", [
    "sshleifer/distilbart-cnn-12-6",
    "google/flan-t5-base",
    "facebook/bart-large-cnn"
])

summarizer = load_summarizer(llm_choice)

# -----------------------------
# Load Model + Filtered Data
# -----------------------------
@st.cache_resource
def load_model_and_data(selected_tag):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    df = pd.read_csv("data/clean_questions_with_answers.csv")

    if 'tags' in df.columns:
        filtered_df = df[df['tags'].str.contains(selected_tag, case=False, na=False)]
        if len(filtered_df) < 50:
            filtered_df = df
    else:
        filtered_df = df[df['title'].str.contains(selected_tag, case=False, na=False)]
        if len(filtered_df) < 50:
            filtered_df = df

    embeddings = model.encode(filtered_df["title"].tolist(), convert_to_tensor=True)
    return model, filtered_df.reset_index(drop=True), embeddings

model, df, question_embeddings = load_model_and_data(selected_tag)

# -----------------------------
# Ask Question View
# -----------------------------
if view_mode == "Ask Question":
    st.title("💬 Tech Community QA Bot")
    st.markdown("Ask a coding question and get the closest Stack Overflow matches + summaries!")

    user_question = st.text_input("🔍 Your Question")

    if user_question:
        with st.spinner("Searching best matches..."):
            user_embedding = model.encode(user_question, convert_to_tensor=True)
            cos_scores = util.pytorch_cos_sim(user_embedding, question_embeddings)[0]
            top_results = cos_scores.topk(num_results)

            agent_decision_log = []

            best_match = None
            raw_answer = ""
            for idx in top_results[1]:
                match = df.iloc[idx.item()]
                answer = match.get('answer', '')
                if isinstance(answer, str) and len(answer.strip().split()) > 3:
                    best_match = match
                    raw_answer = answer
                    break

            if best_match is None:
                agent_decision_log.append("❌ No valid answer found in top results.")
                st.warning("None of the top matches have usable answers. Try changing the tag or your question.")
            else:
                agent_decision_log.append("✅ Valid answer found.")
                if len(raw_answer.split()) > summary_threshold:
                    agent_decision_log.append("📉 Long answer, summarizing with " + llm_choice)
                    truncated = truncate_text(raw_answer)
                    try:
                        summary = summarizer(truncated, max_length=512, min_length=80, do_sample=False)[0]['summary_text']
                    except Exception as e:
                        agent_decision_log.append(f"❌ Summarization failed: {e}")
                        summary = "⚠️ Could not summarize this answer. Try a different one."
                else:
                    summary = raw_answer

                st.success("✅ Best Match Found")
                st.markdown(f"### 🔹 {best_match['title']}")
                st.markdown(f"**Score:** {best_match['score']}")
                st.markdown(f"[🔗 View on Stack Overflow]({best_match['link']})")
                st.markdown("**Answer Summary:**")
                st.info(summary)

            with st.expander(f"🔎 Show Other Top {num_results - 1} Matches"):
                for idx in top_results[1]:
                    match = df.iloc[idx.item()]
                    st.markdown(f"#### 🔸 {match['title']}")
                    st.markdown(f"**Score:** {match['score']}")
                    st.markdown(f"[🔗 View on Stack Overflow]({match['link']})")
                    st.markdown("---")

            with st.expander("🧠 Agent Reasoning Trace"):
                for step in agent_decision_log:
                    st.markdown(f"- {step}")

# -----------------------------
# View Dataset Mode
# -----------------------------
elif view_mode == "Browse Dataset":
    st.title("📚 QA Dataset Viewer")
    st.markdown("View the filtered Stack Overflow questions available to the bot:")
    st.dataframe(df[["title", "score", "link"]], use_container_width=True)
