"""
app.py - Flask Web Server for Sports AI Agent
===============================================
Groq AI (primary) + Wikipedia (fallback)
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

import config
from sports_agent import agent

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html",
        agent_name=config.AGENT_NAME,
        agent_tagline=config.AGENT_TAGLINE)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"success": False, "response": "Empty message."}), 400

    # Check if Groq key is set
    if not agent.ai_available:
        key = config.GROQ_API_KEY
        if not key or key == "YOUR_GROQ_API_KEY_HERE":
            return jsonify({
                "success": False, "needs_key": True,
                "response": "🔑 Set your Groq API key first. Get one free at console.groq.com"
            })

    result = agent.ask(user_message)
    return jsonify(result)


@app.route("/api/check-key", methods=["GET"])
def check_key():
    return jsonify({"valid": agent.ai_available})


@app.route("/api/set-key", methods=["POST"])
def set_key():
    data = request.get_json()
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"success": False}), 400
    config.GROQ_API_KEY = key
    agent.provider = "groq"
    config.AI_PROVIDER = "groq"
    agent._setup_provider()
    return jsonify({"success": agent.ai_available})


@app.route("/api/clear", methods=["POST"])
def clear():
    return jsonify(agent.clear_history())


@app.route("/api/history", methods=["GET"])
def history():
    return jsonify({"history": agent.get_history()})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "agent": config.AGENT_NAME, "ai": agent.ai_available})


if __name__ == "__main__":
    print(f"""
╔═══════════════════════════════════════════════════════╗
║  🏆  {config.AGENT_NAME} - {config.AGENT_TAGLINE}
║  🌐  http://localhost:{config.PORT}
║  ⚡  Groq AI: {'✅ Ready (Llama 3.3 70B)' if agent.ai_available else '❌ Need API Key'}
║  📚  Wikipedia: ✅ Always Available
╚═══════════════════════════════════════════════════════╝
    """)
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
