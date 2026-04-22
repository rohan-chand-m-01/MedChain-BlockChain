"""
Medical Chatbot with conversation memory for WhatsApp.
Uses NVIDIA Llama 3.1 8B for natural conversations.
"""
import os
import logging
import requests
from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')


class MedicalChatbot:
    """
    Medical chatbot with conversation memory.
    Maintains context across multiple messages for natural conversations.
    """
    
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise RuntimeError("NVIDIA_API_KEY not set")
        
        self.base_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.model = "meta/llama-3.1-8b-instruct"
        
        # In-memory conversation storage (phone_number -> messages)
        # In production, use Redis or database
        self.conversations: Dict[str, List[Dict]] = {}
        self.last_activity: Dict[str, datetime] = {}
        
        logger.info("✅ Medical chatbot initialized")
    
    def _clean_old_conversations(self):
        """Remove conversations older than 1 hour."""
        now = datetime.now()
        expired = [
            phone for phone, last_time in self.last_activity.items()
            if now - last_time > timedelta(hours=1)
        ]
        for phone in expired:
            del self.conversations[phone]
            del self.last_activity[phone]
    
    def _get_conversation(self, phone_number: str) -> List[Dict]:
        """Get conversation history for a phone number."""
        self._clean_old_conversations()
        
        if phone_number not in self.conversations:
            # Initialize with system prompt
            self.conversations[phone_number] = [
                {
                    "role": "system",
                    "content": """You are MediChain AI, a friendly medical assistant chatbot. 

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
                }
            ]
        
        return self.conversations[phone_number]
    
    def _add_message(self, phone_number: str, role: str, content: str):
        """Add a message to conversation history."""
        conversation = self._get_conversation(phone_number)
        conversation.append({"role": role, "content": content})
        
        # Keep only last 10 messages (5 exchanges) to stay within token limits
        if len(conversation) > 11:  # 1 system + 10 messages
            self.conversations[phone_number] = [conversation[0]] + conversation[-10:]
        
        self.last_activity[phone_number] = datetime.now()
    
    async def chat(self, phone_number: str, user_message: str, language: str = 'en') -> str:
        """
        Process user message and return chatbot response.
        Maintains conversation context.
        Supports English and Kannada.
        """
        try:
            # Add user message to history
            self._add_message(phone_number, "user", user_message)
            
            # Get full conversation
            conversation = self._get_conversation(phone_number)
            
            # Update system prompt based on language
            if language == 'kn':
                conversation[0]["content"] = """You are MediChain AI, a friendly medical assistant chatbot that responds in Kannada (ಕನ್ನಡ).

Your capabilities:
- Answer medical questions in simple Kannada language
- Explain lab test results and biomarkers
- Provide health information and guidance
- Analyze medical reports (when users send photos/PDFs)

Guidelines:
1. Always respond in Kannada (ಕನ್ನಡ)
2. Be conversational and friendly
3. Use emojis to make responses engaging
4. Keep responses under 800 characters (WhatsApp limit)
5. Always include disclaimer for medical advice
6. Suggest seeing a doctor for specific symptoms
7. Remember context from previous messages

Important:
- You are NOT a replacement for a doctor
- Always recommend professional medical consultation
- Be empathetic and supportive"""
            
            # Call NVIDIA API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": conversation,
                "temperature": 0.8,  # More creative for conversation
                "max_tokens": 500,
                "stream": False
            }
            
            logger.info(f"Sending chat request for {phone_number} in {language} (history: {len(conversation)} messages)")
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Add AI response to history
            self._add_message(phone_number, "assistant", ai_response)
            
            logger.info(f"✓ Chat response sent to {phone_number} in {language}")
            
            return ai_response
            
        except requests.exceptions.Timeout:
            logger.error("NVIDIA API timeout")
            return "⏱️ Sorry, I'm taking too long to respond. Please try again!"
        
        except requests.exceptions.RequestException as e:
            logger.error(f"NVIDIA API error: {e}")
            return "❌ I'm having trouble connecting right now. Please try again in a moment!"
        
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return "❌ Something went wrong. Please try again!"
    
    def reset_conversation(self, phone_number: str):
        """Clear conversation history for a phone number."""
        if phone_number in self.conversations:
            del self.conversations[phone_number]
        if phone_number in self.last_activity:
            del self.last_activity[phone_number]
        logger.info(f"Reset conversation for {phone_number}")


# Global chatbot instance
_chatbot_instance = None


def get_medical_chatbot() -> MedicalChatbot:
    """Get or create the global chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = MedicalChatbot()
    return _chatbot_instance
