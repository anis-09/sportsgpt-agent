"""
sports_agent.py - Sports AI Agent (Groq + Wikipedia fallback)
==============================================================
Primary: Groq API (Llama 3.3 70B - fast & free)
Fallback: Wikipedia (always free, no key needed)
"""

import time
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

import config
from wiki_sports import format_sports_response


@dataclass
class Message:
    role: str
    content: str
    timestamp: str = ""
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%I:%M %p")


class SportsAgent:
    def __init__(self):
        self.conversation_history: List[Message] = []
        self.provider = config.AI_PROVIDER
        self.groq_client = None
        self.ai_available = False
        self._setup_provider()

    def _setup_provider(self):
        """Initialize the AI provider."""
        if self.provider == "groq":
            key = config.GROQ_API_KEY
            if key and key != "YOUR_GROQ_API_KEY_HERE":
                try:
                    from groq import Groq
                    self.groq_client = Groq(api_key=key)
                    self.ai_available = True
                    print(f"✅ Groq AI ready ({config.GROQ_MODEL}) — Fast & Free!")
                except Exception as e:
                    print(f"⚠️ Groq init failed: {e}")
            else:
                print("ℹ️ No Groq API key set — using Wikipedia mode")

        print("✅ Wikipedia Sports Engine ready (always available)")

    def ask(self, user_message: str) -> Dict[str, Any]:
        if not user_message.strip():
            return {"success": False, "response": "Ask me something about sports! 🏆",
                    "timestamp": datetime.now().strftime("%I:%M %p"), "source": "system"}

        user_msg = Message(role="user", content=user_message)
        self.conversation_history.append(user_msg)

        source = "wikipedia"
        try:
            if self.ai_available and self.provider == "groq":
                try:
                    response_text = self._call_groq(user_message)
                    source = "groq"
                except Exception as e:
                    print(f"Groq failed, using Wikipedia: {e}")
                    response_text = self._call_wikipedia(user_message)
            else:
                response_text = self._call_wikipedia(user_message)
        except Exception as e:
            response_text = f"❌ Error: {str(e)}\n\nPlease try again!"

        assistant_msg = Message(role="assistant", content=response_text)
        self.conversation_history.append(assistant_msg)

        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]

        return {"success": True, "response": response_text,
                "timestamp": assistant_msg.timestamp, "source": source}

    def _call_groq(self, message: str) -> str:
        """Call Groq API with Llama model."""
        if not self.groq_client:
            raise Exception("Groq not initialized")

        # Build messages with system prompt + history
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        for msg in self.conversation_history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})

        response = self.groq_client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=messages,
            max_tokens=config.RESPONSE_MAX_TOKENS,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def _call_wikipedia(self, query: str) -> str:
        """Fallback: Fetch sports data from Wikipedia."""
        result = format_sports_response(query)
        return f"🏆 {result}"

    def clear_history(self):
        self.conversation_history = []
        return {"success": True, "message": "Conversation cleared! 🏆"}

    def get_history(self) -> list:
        return [{"role": m.role, "content": m.content, "timestamp": m.timestamp}
                for m in self.conversation_history]


agent = SportsAgent()
