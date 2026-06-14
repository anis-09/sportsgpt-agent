# 🏆 SportsGPT — AI-Powered Sports Intelligence Agent

> **Your Ultimate Sports Expert** — Ask anything about cricket, football, basketball, F1, tennis, Olympics, and 20+ sports!

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?logo=flask)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange?logo=meta)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ⚡ Features

- **🤖 AI-Powered**: Uses Groq API with Llama 3.3 70B for instant, intelligent sports answers
- **📚 Wikipedia Fallback**: Always has answers even without AI — uses Wikipedia's sports database
- **🌍 Bilingual**: Supports English & Hindi/Hinglish naturally
- **🎨 Beautiful UI**: Glassmorphism design with sports-themed aesthetics
- **💬 Chat Interface**: Real-time conversational experience
- **🔑 Dynamic API Key**: Set your Groq API key from the UI — no restart needed
- **🏏⚽🏀🎾🏎️**: Covers Cricket, Football, Basketball, Tennis, F1, Olympics, Boxing, MMA, and many more!

## 🚀 Live Demo

**[👉 Open SportsGPT Live](https://sportsgpt-agent.onrender.com)**

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask (Python) |
| AI Engine | Groq API (Llama 3.3 70B) |
| Fallback | Wikipedia REST API |
| Frontend | HTML/CSS/JavaScript |
| Hosting | Render.com |
| Server | Gunicorn |

## 📦 Setup (Local Development)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/sportsgpt-agent.git
cd sportsgpt-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set API key (get free at https://console.groq.com)
export GROQ_API_KEY="your_key_here"

# Run the app
python app.py
```

Then open http://localhost:5000 🎉

## 🔑 Getting a Groq API Key (Free!)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Create an API key
4. Set it as environment variable or enter it in the app UI

## 📁 Project Structure

```
sportsgpt-agent/
├── app.py              # Flask web server
├── config.py           # Configuration & system prompt
├── sports_agent.py     # AI agent logic (Groq + Wikipedia)
├── wiki_sports.py      # Wikipedia sports data engine
├── requirements.txt    # Python dependencies
├── Procfile           # Render/Heroku deployment
├── runtime.txt        # Python version
├── templates/
│   └── index.html     # Main UI template
└── static/
    ├── css/           # Stylesheets
    └── js/            # Frontend JavaScript
```

## 🌐 Deployment on Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `gunicorn app:app`
6. Add Environment Variable: `GROQ_API_KEY` = your key
7. Deploy! 🚀

---

**Built with ❤️ by Anis Akhtar** | Powered by Groq AI & Wikipedia
