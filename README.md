# 🧠 Exam Anxiety Detector

> **AI-Based Intelligent Mental Wellness Support System for Students**

An AI-powered web application that helps students understand and manage pre-exam anxiety using NLP, BERT classification, and Google Gemini AI.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Features

- **Anxiety Level Detection** — BERT-based NLP model classifies text into Low / Moderate / High anxiety
- **Personalized Tips** — AI-generated coping strategies tailored to your anxiety level
- **NLP Analysis** — Sentiment analysis, keyword extraction, named entity recognition
- **AI Chat Counselor** — Multi-turn supportive chat powered by Google Gemini
- **Privacy-First** — No personal data stored, fully anonymous sessions
- **Interactive UI** — Beautiful Streamlit interface with calming design

## 🖥️ Screenshots

### Home — Anxiety Analysis
The main interface where students share their pre-exam thoughts and receive AI-powered analysis.

### Results — Color-coded anxiety levels with personalized tips
- 🟢 **Low Anxiety** — Encouraging reinforcement
- 🟡 **Moderate Anxiety** — Breathing exercises & study strategies  
- 🔴 **High Anxiety** — Calming techniques & counselor referral

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/exam-anxiety-detector.git
cd exam-anxiety-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('vader_lexicon')"

# Copy environment file
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

**Start the Flask API server:**
```bash
python run.py
```
The API will be available at `http://localhost:8080` with Swagger docs at `http://localhost:8080/docs`.

**Start the Streamlit frontend (in a new terminal):**
```bash
streamlit run frontend/app.py
```
The UI will open at `http://localhost:8501`.

### Docker

```bash
# Build and run
docker-compose up --build

# Or just the API
docker build -t exam-anxiety-app .
docker run -p 8080:8080 --env-file .env exam-anxiety-app
```

---

## 🏗️ Architecture

```
exam-anxiety-detector/
├── app/                    # Flask backend
│   ├── __init__.py         # App factory
│   ├── routes/             # API endpoints
│   │   ├── ai_routes.py    # /api/v1/ai/*
│   │   ├── nlp_routes.py   # /api/v1/nlp/*
│   │   └── health_routes.py
│   ├── services/           # Business logic
│   │   ├── bert_classifier.py
│   │   ├── nlp_service.py
│   │   └── gemini_service.py
│   ├── models/schemas.py   # Request/response models
│   └── utils/              # Auth, validation, tips
├── frontend/app.py         # Streamlit UI
├── tests/                  # Pytest suite
├── ml/                     # Model training code
├── config.py               # App configuration
├── run.py                  # Entry point
├── Dockerfile
└── docker-compose.yml
```

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/health/` | System health check | No |
| GET | `/api/v1/health/model` | Model readiness | No |
| POST | `/api/v1/ai/analyze` | Anxiety classification | API Key |
| POST | `/api/v1/ai/chat` | Gemini chat session | API Key |
| POST | `/api/v1/ai/summarize` | Text summarization | API Key |
| POST | `/api/v1/nlp/analyze` | Full NLP pipeline | API Key |
| POST | `/api/v1/nlp/sentiment` | Sentiment only | API Key |
| POST | `/api/v1/nlp/entities` | Named entities | API Key |
| POST | `/api/v1/nlp/keywords` | Keyword extraction | API Key |

### Example Request

```bash
curl -X POST http://localhost:8080/api/v1/ai/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{"text": "I am really nervous about my final exam tomorrow"}'
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## ⚙️ Configuration

Set these environment variables in `.env`:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key | Yes |
| `APP_API_KEY` | API authentication key | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key | Optional* |
| `FLASK_ENV` | `development` / `production` | Yes |
| `GEMINI_MODEL` | Gemini model name | No |
| `BERT_MODEL` | BERT model identifier | No |

*Gemini features (chat, summarize, AI tips) require a Google API key.

---

## ⚠️ Ethical Disclaimers

- **This tool is non-diagnostic.** It provides general wellness suggestions only.
- **No PII is stored.** Student text is never linked to an identity.
- **Counselor referral** is included for all High Anxiety results.
- **Transparency** — Users are always informed AI is analyzing their text.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

*Built with ❤️ for student wellness · March 2026*
