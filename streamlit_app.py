"""Standalone Streamlit app for deployment on Streamlit Community Cloud.
This version includes built-in analysis without requiring a separate Flask server."""

import streamlit as st
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.nlp_service import NLPService
from app.services.bert_classifier import BertClassifier
from app.utils.validators import validate_text_input
from app.utils.tips_content import ANXIETY_TIPS, DISCLAIMER

# --- Initialize services (cached) ---
@st.cache_resource
def load_nlp_service():
    return NLPService()

@st.cache_resource
def load_classifier():
    return BertClassifier()

nlp_svc = load_nlp_service()
classifier = load_classifier()

# --- Page Config ---
st.set_page_config(
    page_title="Exam Anxiety Detector",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main { background-color: #f0f7f4; }
    .stApp { font-family: 'Segoe UI', sans-serif; }
    
    .result-card {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .result-green { background: linear-gradient(135deg, #d4edda, #c3e6cb); border-left: 5px solid #28a745; }
    .result-yellow { background: linear-gradient(135deg, #fff3cd, #ffeaa7); border-left: 5px solid #ffc107; }
    .result-red { background: linear-gradient(135deg, #f8d7da, #f5c6cb); border-left: 5px solid #dc3545; }
    
    .tip-card {
        background: white;
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #4a90d9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .disclaimer {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.85rem;
    }
    
    .header-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("🧠 Exam Anxiety Detector")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📊 NLP Analysis", "ℹ️ About"],
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    st.markdown(
        '<div class="disclaimer">'
        "⚠️ <strong>Important:</strong> This tool provides general wellness "
        "suggestions only. It is NOT a medical or psychological diagnosis."
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.caption("v1.0 · March 2026")
    st.caption("Built with ❤️ for student wellness")


# ==================== HOME PAGE ====================
if page == "🏠 Home":
    st.markdown(
        '<div class="header-banner">'
        "<h1>🧠 Exam Anxiety Detector</h1>"
        "<p>AI-powered mental wellness support for students</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### 📝 Share Your Pre-Exam Thoughts")
    st.markdown("Tell us how you're feeling about your upcoming exams. Our AI will analyze your text and provide personalized support.")

    consent = st.checkbox(
        "I understand this tool provides general wellness suggestions only and is not a medical diagnosis. "
        "My text will be analyzed by AI and will not be stored or linked to my identity.",
        value=False,
    )

    text_input = st.text_area(
        "How are you feeling about your exams?",
        height=180,
        max_chars=10000,
        placeholder="Example: I have my final exams next week and I'm feeling really nervous. I can't concentrate on studying and keep thinking I'm going to fail...",
    )

    char_count = len(text_input) if text_input else 0
    col_count, col_btn = st.columns([3, 1])
    with col_count:
        color = "green" if char_count >= 50 else "red"
        st.markdown(f":{color}[{char_count} / 10,000 characters]")
        if 0 < char_count < 50:
            st.caption("Please write at least 50 characters for better analysis.")
    
    with col_btn:
        analyze_btn = st.button("🔍 Analyze My Anxiety", type="primary", use_container_width=True, disabled=not consent or char_count < 50)

    if analyze_btn and text_input and consent:
        with st.spinner("🧠 Analyzing your text..."):
            try:
                cleaned_text = validate_text_input(text_input)
                prediction = classifier.predict(cleaned_text)
                label = prediction["label"]
                confidence = prediction["confidence"]
                tips_data = ANXIETY_TIPS.get(label, ANXIETY_TIPS["Moderate Anxiety"])

                st.markdown("---")
                st.markdown("### 📊 Analysis Results")

                css_class = f"result-{tips_data['color']}"
                emoji = tips_data["emoji"]

                st.markdown(
                    f'<div class="result-card {css_class}">'
                    f"<h2>{emoji} {label}</h2>"
                    f"<p>Confidence: <strong>{confidence * 100:.1f}%</strong></p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                # Score breakdown
                st.markdown("#### Probability Breakdown")
                for score in prediction.get("all_scores", []):
                    score_label = score["label"]
                    score_val = score["score"]
                    
                    col_label, col_bar = st.columns([1, 3])
                    with col_label:
                        st.markdown(f"**{score_label}**")
                    with col_bar:
                        st.progress(min(max(score_val, 0.0), 1.0))
                        st.caption(f"{score_val * 100:.1f}%")

                # NLP Insight
                nlp_result = nlp_svc.analyze(cleaned_text)
                sentiment = nlp_result.get("sentiment", {})
                st.markdown(f"#### 😊 Sentiment: **{sentiment.get('label', 'neutral').capitalize()}** (compound: {sentiment.get('compound', 0):.3f})")

                keywords = nlp_result.get("keywords", [])
                if keywords:
                    st.markdown(f"#### 🔑 Key Themes: {', '.join(keywords[:5])}")

                # Tips
                st.markdown("#### 💡 Personalized Tips")
                for tip in tips_data["tips"]:
                    st.markdown(
                        f'<div class="tip-card">💡 {tip}</div>',
                        unsafe_allow_html=True,
                    )

                if label == "High Anxiety":
                    st.warning("🆘 **We strongly recommend reaching out to your institution's counseling service.** You don't have to face this alone.")

                st.markdown(
                    f'<div class="disclaimer">{DISCLAIMER}</div>',
                    unsafe_allow_html=True,
                )

            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")


# ==================== NLP ANALYSIS PAGE ====================
elif page == "📊 NLP Analysis":
    st.markdown("### 📊 Detailed NLP Analysis")
    st.markdown("Get a deep linguistic analysis of your text including sentiment, entities, and keywords.")

    nlp_text = st.text_area("Enter text for NLP analysis:", height=150, max_chars=10000)

    if st.button("🔬 Run NLP Analysis", type="primary") and nlp_text:
        with st.spinner("Processing..."):
            try:
                cleaned = validate_text_input(nlp_text)
                data = nlp_svc.analyze(cleaned)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 😊 Sentiment Analysis")
                    sentiment = data.get("sentiment", {})
                    label = sentiment.get("label", "neutral")
                    compound = sentiment.get("compound", 0)
                    emoji_map = {"positive": "😊", "negative": "😟", "neutral": "😐"}
                    st.markdown(f"**{emoji_map.get(label, '😐')} {label.capitalize()}** (compound: {compound:.3f})")

                    scores = sentiment.get("scores", {})
                    for key, val in scores.items():
                        if key != "compound":
                            st.progress(val, text=f"{key}: {val:.3f}")

                with col2:
                    st.markdown("#### 🔑 Keywords")
                    keywords = data.get("keywords", [])
                    if keywords:
                        st.markdown(" ".join([f"`{kw}`" for kw in keywords]))
                    else:
                        st.caption("No significant keywords found.")

                st.markdown("#### 🏷️ Named Entities")
                entities = data.get("entities", [])
                if entities:
                    for ent in entities:
                        st.markdown(f"- **{ent['text']}** ({ent['label']})")
                else:
                    st.caption("No named entities found.")

            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")


# ==================== ABOUT PAGE ====================
elif page == "ℹ️ About":
    st.markdown("### ℹ️ About This Tool")

    st.markdown("""
    **Exam Anxiety Detector** is an AI-powered mental wellness support system designed 
    to help students understand and manage pre-exam anxiety.
    
    #### 🎯 How It Works
    1. **Share your thoughts** — Write about how you're feeling before exams
    2. **AI Analysis** — Our NLP models analyze your text for anxiety indicators
    3. **Get Support** — Receive personalized tips and strategies
    
    #### 🤖 Technology Stack
    - **BERT** — Deep learning model for anxiety level classification
    - **NLTK & spaCy** — Natural language processing for text analysis
    - **Google Gemini AI** — Generative AI for personalized tips and chat
    - **Flask** — Backend API server
    - **Streamlit** — Interactive web interface
    
    #### ⚠️ Important Disclaimers
    - This tool is **NOT** a medical or psychological diagnosis tool
    - Results are AI-generated suggestions, not professional advice
    - No personal data is stored or linked to your identity
    - For severe anxiety, please contact a qualified mental health professional
    
    #### 🔒 Privacy
    - Your text is processed in real-time and **not stored**
    - No personal identifiable information (PII) is collected
    - All sessions are anonymous
    
    #### 📬 Contact
    If your institution is interested in a pilot program, please reach out to the project team.
    """)

    st.markdown("---")
    st.markdown(
        '<div class="disclaimer">'
        "⚠️ If you are experiencing severe anxiety or emotional distress, "
        "please reach out to a qualified mental health professional or your "
        "institution's counseling service immediately."
        "</div>",
        unsafe_allow_html=True,
    )
