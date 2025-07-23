import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import torch

MAX_TOKENS = 1024  # BART input limit

def truncate_text(text, max_tokens=MAX_TOKENS):
    return " ".join(text.split()[:max_tokens])

# -----------------------------
# Load Summarization Model
# -----------------------------
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

summarizer = load_summarizer()

# -----------------------------
# Sidebar Configuration
# -----------------------------
st.sidebar.title("⚙️ Configuration")

view_mode = st.sidebar.radio("Select View Mode", ["Ask Question", "Browse Dataset"])
selected_tag = st.sidebar.selectbox("Filter Questions by Tag", ["python", "javascript", "flask", "django", "c++", "java"])
num_results = st.sidebar.slider("Top N Matches to Compare", 3, 20, 10)
summary_threshold = st.sidebar.slider("Minimum Words Before Summarizing", 60, 300, 80)
show_debug = st.sidebar.checkbox("🔧 Show Debug Info", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("Model: `all-MiniLM-L6-v2`")

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

            try:
                best_idx = top_results[1][0].item()
                best_match = df.iloc[best_idx]
                raw_answer = best_match['answer'] if pd.notnull(best_match['answer']) else ""

                if show_debug:
                    st.code(raw_answer[:500], language="text")

                if raw_answer and len(raw_answer.split()) > 10:
                    agent_decision_log.append("✅ Valid answer found.")
                    if len(raw_answer.split()) > summary_threshold:
                        agent_decision_log.append("📉 Long answer, summarizing.")
                        truncated = truncate_text(raw_answer)
                        try:
                            summary_output = summarizer(truncated, max_length=512, min_length=80, do_sample=False)
                            summary = summary_output[0]['summary_text'] if summary_output else "⚠️ Could not summarize this answer."
                        except Exception as e:
                            summary = "⚠️ Could not summarize this answer. Try a different one."
                            agent_decision_log.append(f"❌ Summarization failed: {str(e)}")
                            if show_debug:
                                st.error(f"Summarization Exception: {e}")
                    else:
                        summary = raw_answer
                else:
                    agent_decision_log.append("⚠️ No valid answer. Check other suggestions.")
                    summary = "No valid answer found. Try rephrasing or exploring other matches."

                # Display
                st.success("✅ Best Match Found")
                st.markdown(f"### 🔹 {best_match['title']}")
                st.markdown(f"**Score:** {best_match['score']}")
                st.markdown(f"[🔗 View on Stack Overflow]({best_match['link']})")
                st.markdown("**Answer Summary:**")
                st.info(summary)

                with st.expander(f"🔎 Show Other Top {num_results - 1} Matches"):
                    for idx in top_results[1][1:]:
                        match = df.iloc[idx.item()]
                        st.markdown(f"#### 🔸 {match['title']}")
                        st.markdown(f"**Score:** {match['score']}")
                        st.markdown(f"[🔗 View on Stack Overflow]({match['link']})")
                        st.markdown("---")

                with st.expander("🧠 Agent Reasoning Trace"):
                    for step in agent_decision_log:
                        st.markdown(f"- {step}")

            except IndexError:
                st.warning("⚠️ Could not retrieve results. Please try a different question.")

# -----------------------------
# View Dataset Mode
# -----------------------------
elif view_mode == "Browse Dataset":
    st.title("📚 QA Dataset Viewer")
    st.markdown("View the filtered Stack Overflow questions available to the bot:")
    st.dataframe(df[["title", "score", "link"]], use_container_width=True)
