import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import torch
import datetime

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

view_mode = st.sidebar.radio("Select View Mode", ["Ask Question", "Browse Dataset", "VectorDB Insights"])
selected_tag = st.sidebar.selectbox("Filter Questions by Tag", ["python", "javascript", "flask", "django", "c++", "java"])
summary_threshold = st.sidebar.slider("Minimum Words Before Summarizing", 60, 300, 80)

st.sidebar.markdown("---")
st.sidebar.markdown("Model: `all-MiniLM-L6-v2`")

llm_display_names = {
    "DistilBART": "sshleifer/distilbart-cnn-12-6",
    "FLAN-T5": "google/flan-t5-base",
    "BART-Large": "facebook/bart-large-cnn"
}

llm_name_selected = st.sidebar.selectbox("Choose LLM for Summarization", list(llm_display_names.keys()))
llm_choice = llm_display_names[llm_name_selected]

summarizer = load_summarizer(llm_choice)

with st.sidebar.expander("📜 Search History"):
    if st.session_state.get("search_history"):
        for item in reversed(st.session_state["search_history"][-5:]):  # Show last 5
            st.markdown(f"**🕒 {item['timestamp']}**")
            st.markdown(f"🔍 *{item['question']}*")
            st.markdown(f"🔗 [{item['matched_title']}]({item['link']})")
            st.markdown("---")
    else:
        st.markdown("No searches yet.")

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
            top_results = cos_scores.topk(10)

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
                    agent_decision_log.append(f"📉 Long answer, summarizing with {llm_name_selected}")
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

                if "search_history" not in st.session_state:
                    st.session_state["search_history"] = []

                st.session_state["search_history"].append({
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "question": user_question,
                    "matched_title": best_match['title'],
                    "link": best_match['link']
                })

# -----------------------------
# View Dataset Mode
# -----------------------------
elif view_mode == "Browse Dataset":
    st.title("📚 QA Dataset Viewer")
    st.markdown("View the filtered Stack Overflow questions available to the bot:")
    st.dataframe(df[["title", "score", "link"]], use_container_width=True)

# -----------------------------
# VectorDB Insights Mode
# -----------------------------
elif view_mode == "VectorDB Insights":
    st.title("🧐 VectorDB Insights")
    st.markdown("Explore vector embeddings and similarity scores used in the QA Bot.")

    st.markdown("### 📌 Loaded Tags:")
    st.code(selected_tag)

    st.markdown("### 🔹 Number of Questions Loaded:")
    st.code(len(df))

    st.markdown("### 🔍 View Vector Embeddings")
    with st.expander("📊 View Embedding Vector for First 5 Questions"):
        for idx in range(min(5, len(df))):
            st.markdown(f"**Q{idx+1}:** {df.iloc[idx]['title']}")
            st.code(question_embeddings[idx].tolist(), language='json')

    st.markdown("### 📈 Test a Similarity Query")
    test_question = st.text_input("🔍 Enter a sample question to test similarity:")
    if test_question:
        test_embedding = model.encode(test_question, convert_to_tensor=True)
        similarity_scores = util.pytorch_cos_sim(test_embedding, question_embeddings)[0]

        top_k = similarity_scores.topk(5)
        st.markdown("#### 🔝 Top 5 Matches by Cosine Similarity:")
        for i, idx in enumerate(top_k[1]):
            score = top_k[0][i].item()
            title = df.iloc[idx.item()]['title']
            st.markdown(f"**{i+1}.** `{score:.4f}` → {title}")
