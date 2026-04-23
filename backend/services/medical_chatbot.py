"""
Medical Chatbot with conversation memory for WhatsApp.
Exclusively uses Ollama MedGemma 4B (local model) — no external API calls.
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta

from services.ollama_medgemma import get_ollama_client

logger = logging.getLogger(__name__)


class MedicalChatbot:
    """
    Medical chatbot with conversation memory.
    Maintains context across multiple messages for natural conversations.
    Powered exclusively by local Ollama MedGemma 4B.
    """

    SYSTEM_PROMPT_EN = """You are MediChain AI, a friendly medical assistant chatbot powered by MedGemma.

Your capabilities:
- Answer medical questions in simple language
- Explain lab test results and biomarkers
- Provide health information and guidance
- Analyze medical reports (when users send photos/PDFs)

Guidelines:
1. Be conversational and friendly
2. Use emojis to make responses engaging
3. Keep responses under 800 characters (WhatsApp limit)
4. Always include disclaimer for medical advice
5. Suggest seeing a doctor for specific symptoms
6. Remember context from previous messages
7. If user asks about their report, remind them to send a photo/PDF

Important:
- You are NOT a replacement for a doctor
- Always recommend professional medical consultation
- Be empathetic and supportive"""

    SYSTEM_PROMPT_KN = """You are MediChain AI, a friendly medical assistant chatbot that responds in Kannada (ಕನ್ನಡ), powered by MedGemma.

Your capabilities:
- Answer medical questions in simple Kannada language
- Explain lab test results and biomarkers
- Provide health information and guidance

Guidelines:
1. Always respond in Kannada (ಕನ್ನಡ)
2. Be conversational and friendly
3. Use emojis to make responses engaging
4. Keep responses under 800 characters (WhatsApp limit)
5. Always include disclaimer for medical advice
6. Suggest seeing a doctor for specific symptoms

Important:
- You are NOT a replacement for a doctor
- Always recommend professional medical consultation
- Be empathetic and supportive"""

    def __init__(self):
        self._ollama = get_ollama_client()

        # In-memory conversation storage: phone_number -> List[Dict]
        self.conversations: Dict[str, List[Dict]] = {}
        self.last_activity: Dict[str, datetime] = {}

        if self._ollama.is_available():
            logger.info("✅ Medical chatbot ready — Ollama MedGemma 4B (local)")
        else:
            logger.warning("⚠️  Ollama MedGemma not available. Start Ollama and run: ollama pull medgemma:4b")

    # ------------------------------------------------------------------
    # Conversation management
    # ------------------------------------------------------------------

    def _clean_old_conversations(self):
        """Remove conversations inactive for more than 1 hour."""
        now = datetime.now()
        expired = [
            phone for phone, last_time in self.last_activity.items()
            if now - last_time > timedelta(hours=1)
        ]
        for phone in expired:
            del self.conversations[phone]
            del self.last_activity[phone]

    def _get_conversation(self, phone_number: str, language: str = 'en') -> List[Dict]:
        """Get or initialise conversation history for a phone number."""
        self._clean_old_conversations()

        if phone_number not in self.conversations:
            system_prompt = self.SYSTEM_PROMPT_KN if language == 'kn' else self.SYSTEM_PROMPT_EN
            self.conversations[phone_number] = [
                {"role": "system", "content": system_prompt}
            ]

        return self.conversations[phone_number]

    def _add_message(self, phone_number: str, role: str, content: str):
        """Append a message and trim history to last 10 exchanges."""
        conversation = self.conversations[phone_number]
        conversation.append({"role": role, "content": content})

        # Keep system prompt + last 10 messages
        if len(conversation) > 11:
            self.conversations[phone_number] = [conversation[0]] + conversation[-10:]

        self.last_activity[phone_number] = datetime.now()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(self, phone_number: str, user_message: str, language: str = 'en') -> str:
        """
        Process a user message and return MedGemma's response.
        Maintains full conversation context per phone number.
        """
        if not self._ollama.is_available():
            return "❌ MedGemma local model is not running. Please contact support."

        # Initialise / retrieve conversation
        self._get_conversation(phone_number, language)
        self._add_message(phone_number, "user", user_message)

        conversation = self.conversations[phone_number]

        try:
            logger.info(f"[MedGemma] Chat for {phone_number} | lang={language} | history={len(conversation)} msgs")
            response = self._ollama._chat(conversation, temperature=0.7, max_tokens=500)
            self._add_message(phone_number, "assistant", response)
            logger.info(f"✓ [MedGemma] Response sent to {phone_number}")
            return response

        except Exception as e:
            logger.error(f"[MedGemma] Chat error for {phone_number}: {e}")
            return "❌ Something went wrong with the AI. Please try again!"

    def reset_conversation(self, phone_number: str):
        """Clear conversation history for a phone number."""
        self.conversations.pop(phone_number, None)
        self.last_activity.pop(phone_number, None)
        logger.info(f"Reset conversation for {phone_number}")


# ------------------------------------------------------------------
# Singleton
# ------------------------------------------------------------------

_chatbot_instance: MedicalChatbot | None = None


def get_medical_chatbot() -> MedicalChatbot:
    """Get or create the global chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = MedicalChatbot()
    return _chatbot_instance
