# 🧠 AI-Powered Smart Interview Simulation & Feedback Engine

[![Live Demo](https://img.shields.io/badge/Demo-Live%20Platform-brightgreen?style=for-the-badge&logo=django&logoColor=white)](https://ai-interview-engine.onrender.com)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/keerthana22r-oss/ai-interview-simulation--engine)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%20%2F%204.2-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Google Gemini](https://img.shields.io/badge/AI%20Engine-Gemini%20API-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com/)
[![OpenAI](https://img.shields.io/badge/AI%20Engine-OpenAI%20GPT-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
[![SQLite / Postgres](https://img.shields.io/badge/Database-SQLite%20%2F%20PostgreSQL-003B57?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Frontend-Bootstrap%205-7952B3?style=flat-square&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

---

## 📌 Executive Overview

The **AI-Powered Smart Interview Simulation & Feedback Engine** is a full-stack automated technical and behavioral interview platform built on **Django**. It replicates real-world hiring loops by dynamically generating role-tailored technical, system design, HR, and behavioral interview questions using state-of-the-art Large Language Models (**Google Gemini** and **OpenAI GPT**).

Candidates participate in time-bounded interview sessions, submitting structured responses that are automatically evaluated across multiple dimensions: **Technical Accuracy (0–100)**, **Communication Clarity**, **Structure & Articulation**, and **Confidence**. The platform provides candidates with an in-depth scorecard, highlighted keyword matches, identified blind spots, ideal reference answers, and a targeted improvement roadmap.

---

## 🎯 Live Application & Reviewer Walkthrough

> [!TIP]
> **Experience the Live Simulation:** Navigate to **[ai-interview-engine.onrender.com](https://ai-interview-engine.onrender.com)** *(or your designated cloud host)*.
> - **Demo User:** `candidate@interview-ai.local`
> - **Demo Password:** `InterviewReady2026!`

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AI INTERVIEW SCORECARD & FEEDBACK REPORT                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Candidate: Keerthana K R  ·  Target Role: Full-Stack Engineer  ·  Domain: Technical    │
│ Overall Score: 88.5 / 100 [PASSED]  ·  Duration: 24m 12s                               │
├──────────────────────┬──────────────────────┬───────────────────┬──────────────────────┤
│ 💻 Technical         │ 🗣️ Communication     │ 📐 Structure      │ ⚡ Confidence        │
│      90 / 100        │      85 / 100        │     88 / 100      │      91 / 100        │
├──────────────────────┴──────────────────────┴───────────────────┴──────────────────────┤
│ 💡 AI Summary:                                                                         │
│ Strong grasp of Django ORM indexing, RESTful pagination, and database normalization.  │
│                                                                                        │
│ 🎯 Strengths:                                                                          │
│  • Clearly explained difference between LEFT JOIN and INNER JOIN performance.          │
│  • Emphasized security sanitization against SQL injection and CSRF attacks.            │
│                                                                                        │
│ ⚠️ Areas for Improvement:                                                             │
│  • Mention caching strategies (Redis / Memcached) when designing high-throughput APIs.│
│                                                                                        │
│ 📖 Recommended Resources:                                                             │
│  • High-Performance Django Architecture Guide · System Design Primer                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features & Architectural Highlights

- **🎯 Multi-Domain & Multi-Role Simulation**:
  - Supports **Technical**, **System Design**, **Behavioral (STAR method)**, and **HR** domains.
  - Dynamically configures questions based on experience tier: `Fresher`, `Junior`, `Mid-Level`, and `Senior`.
- **⚡ Dynamic AI Question Synthesizer**:
  - Prompts LLMs (Gemini / OpenAI) with candidate skills, target role description, and difficulty to generate non-repetitive, context-aware interview questions.
- **🔍 Multi-Dimensional Answer Evaluator**:
  - Scores responses against expected technical keywords.
  - Returns itemized critique: `Missing Points`, `Matched Concepts`, and generates an **Ideal Model Answer** for comparison.
- **📊 Comprehensive Feedback Report**:
  - Generates downloadable post-interview diagnostic reports with actionable study resources.
- **🛡️ Enterprise AI Observability & Token Auditing**:
  - Includes a dedicated `AIProviderLog` engine recording latency in milliseconds (`latency_ms`), prompt/completion tokens, model names, and JSON request/response payloads.

---

## 🛠️ Technology Stack Breakdown

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend Framework** | **Python 3 / Django** | MVT pattern, Custom User model, UUID primary keys, Django ORM |
| **LLM Orchestration** | **Google Gemini & OpenAI** | Pluggable AI provider architecture with JSON schema validation |
| **Database** | **SQLite / PostgreSQL** | Relational schema with indexed querysets and cascading relationships |
| **Frontend UI** | **HTML5, CSS3, Bootstrap 5** | Clean assessment UI with responsive question pagination and timers |
| **Observability** | **AIProviderLog** | In-app token counting, API latency profiling, and error auditing |

---

## 🏛️ System Architecture & Directory Tree

```
ai-interview-simulation--engine/
├── README.md                     # Comprehensive Project Documentation
├── .gitignore                    # Environment & credential protection
├── myproject/
│   ├── manage.py                 # Django management utility
│   ├── db.sqlite3                # Local development database
│   ├── myproject/                # Core settings, WSGI/ASGI, root URL routing
│   │   ├── .env.example          # Safe configuration template
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── base/                     # Core Interview Engine App
│       ├── models.py             # Domain models (Session, Question, Answer, FeedbackReport, AIProviderLog)
│       ├── views.py              # Session lifecycle, AI prompt dispatch, scoring views
│       ├── forms.py              # Candidate answer submission & profile forms
│       ├── urls.py               # Route declarations
│       ├── templates/            # Assessment interface, feedback reports, dashboards
│       └── static/               # CSS, JS timers, responsive UI assets
```

---

## 📡 Core Data Models

```
┌─────────────────┐       ┌────────────────────┐       ┌───────────────────┐
│     User        ├──────►│  InterviewSession  ├──────►│  FeedbackReport   │
│ (Custom Auth)   │  1:N  │ (Scores & Status)  │  1:1  │(Summary & Roadmap)│
└─────────────────┘       └─────────┬──────────┘       └───────────────────┘
                                    │ 1:N
                                    ▼
                          ┌────────────────────┐
                          │ InterviewQuestion  │
                          └─────────┬──────────┘
                                    │ 1:1
                                    ▼
                          ┌────────────────────┐
                          │  InterviewAnswer   │
                          │(Evaluation & Ideal)│
                          └────────────────────┘
```

---

## 💻 Local Development & Quickstart Guide

### Prerequisites
- **Python 3.10+**
- A free API key from [Google AI Studio](https://aistudio.google.com/apikey) **OR** [OpenAI Platform](https://platform.openai.com/).

### 1. Clone the Repository
```bash
git clone https://github.com/keerthana22r-oss/ai-interview-simulation--engine.git
cd ai-interview-simulation--engine/myproject
```

### 2. Setup Virtual Environment
```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install django google-genai openai python-decouple
```

### 3. Configure Environment Variables
Create a `.env` file inside `myproject/myproject/` using the template:
```ini
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key
GEMINI_API_KEY=your_gemini_key_here
# OPENAI_API_KEY=sk-...
```

### 4. Migrate Database & Launch Server
```bash
# Run database migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Open **`http://127.0.0.1:8000`** in your browser.

---

## 🚀 One-Click Cloud Deployment (Render / Railway)

1. Connect your repository to **Render** or **Railway**.
2. Specify build command:
   ```bash
   pip install -r requirements.txt && python myproject/manage.py collectstatic --no-input
   ```
3. Specify start command:
   ```bash
   gunicorn myproject.wsgi:application --chdir myproject
   ```
4. Add `GEMINI_API_KEY` and `SECRET_KEY` in the cloud environment dashboard.

---

## 🔮 Roadmap & Future Enhancements

- [ ] **Speech-to-Text & Audio Delivery**: Integrate Whisper API / Web Speech API for voice-driven conversational mock interviews.
- [ ] **Real-time Video & Eye-Tracking**: Analyze webcam eye-contact and posture confidence using MediaPipe.
- [ ] **Live Code Execution Sandbox**: Embed a Monaco code editor with Pyodide / Docker sandbox for real-time coding challenges.

---

## 👩‍💻 Author & Contact

**Keerthana K R**  
Full-Stack & AI Software Engineer  

- **GitHub:** [@keerthana22r-oss](https://github.com/keerthana22r-oss)
- **Email:** [keerthana22r@gmail.com](mailto:keerthana22r@gmail.com)
- **LinkedIn:** [linkedin.com/in/keerthana-k-r-9907aa3a8](http://www.linkedin.com/in/keerthana-k-r-9907aa3a8)

---

## 📄 License

This project is open-source and distributed under the [MIT License](https://opensource.org/licenses/MIT).
