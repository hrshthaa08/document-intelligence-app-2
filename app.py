import streamlit as st
import pdfplumber
import yake
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from collections import Counter

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Document Intelligence Platform",
    layout="wide"
)

# ---------------- UI ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #020617, #0f172a);
}
.main {
    color: #e2e8f0;
}
.header-box {
    background: linear-gradient(90deg,#1e3a8a,#2563eb);
    padding:20px;
    border-radius:12px;
    text-align:center;
    color:white;
    font-size:24px;
}
.card {
    background: rgba(255,255,255,0.05);
    padding:20px;
    border-radius:12px;
    margin-bottom:15px;
}
.stButton>button {
    background: linear-gradient(90deg,#2563eb,#3b82f6);
    color:white;
    border-radius:8px;
}
section[data-testid="stSidebar"] {
    background-color: #020617;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class='header-box'>
🛡️ Enterprise Document Intelligence Platform  
<br><small>AI-Powered Unstructured Data Analysis System</small>
</div>
<br>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Configuration")

# Allow up to 500 keywords
num_keywords = st.sidebar.slider("Keyword Depth", 10, 500, 100)

# ---------------- FUNCTIONS ----------------
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + " "
    return text

# 🔥 IMPROVED KEYWORD EXTRACTION
def get_keywords(text):
    kw_extractor = yake.KeywordExtractor(top=600)
    keywords = kw_extractor.extract_keywords(text)

    # sort by importance
    keywords = sorted(keywords, key=lambda x: x[1])

    cleaned = []
    for kw, score in keywords:
        if len(kw) > 3 and kw.lower() not in cleaned:
            cleaned.append(kw.lower())

    return cleaned[:num_keywords]

def summarize(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)
    return " ".join([str(sentence) for sentence in summary])

def highlight(text, keywords):
    for word in keywords[:20]:
        text = text.replace(word, f"**{word}**")
    return text

def smart_answer(question, text):
    sentences = text.split(".")
    for sentence in sentences:
        if any(word.lower() in sentence.lower() for word in question.split()):
            return sentence.strip()
    return "No relevant answer found. Try rephrasing."

# ---------------- UPLOAD ----------------
st.markdown("### 📂 Upload Document")
file = st.file_uploader("Upload PDF", type=["pdf"])

if file:
    with st.spinner("🔍 Processing document..."):
        text = extract_text(file)

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🧠 Insights", "📜 Preview", "🤖 Assistant"])

    # DASHBOARD
    with tab1:
        col1, col2, col3 = st.columns(3)
        col1.metric("Characters", len(text))
        col2.metric("Words", len(text.split()))
        col3.metric("Keywords", num_keywords)

        st.markdown("### 📈 Keyword Frequency")
        words = text.lower().split()
        freq = Counter(words)
        st.bar_chart(dict(freq.most_common(10)))

    # INSIGHTS
    with tab2:
        st.markdown("### 🔑 Key Terms Extraction")

        keywords = get_keywords(text)

        # Show only top 20 (clean UI)
        st.write(keywords[:20])

        st.info(f"Total Keywords Extracted: {len(keywords)}")

        st.markdown("### 🧠 Summary")
        st.success(summarize(text))

        st.markdown("### ✨ Highlighted Content")
        st.markdown(highlight(text[:2000], keywords))

    # PREVIEW
    with tab3:
        st.markdown("### 📜 Document Preview")
        st.info(text[:2000])

    # CHATBOT
    with tab4:
        st.markdown("### 🤖 Intelligent Assistant")

        if "chat" not in st.session_state:
            st.session_state.chat = []

        question = st.text_input("Ask about the document")

        if question:
            answer = smart_answer(question, text)
            st.session_state.chat.append((question, answer))

        for q, a in st.session_state.chat:
            st.markdown(f"**You:** {q}")
            st.markdown(f"**System:** {a}")

    st.download_button("⬇ Download Output", text)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("© 2026 Document Intelligence Platform | Internship Project")