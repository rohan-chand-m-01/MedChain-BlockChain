"""
WhatsApp Internationalization (i18n) Support
Detects language and provides translations for Kannada and English
Stores user language preferences
"""
import re
from typing import Dict, Tuple

# Kannada Unicode range: \u0C80-\u0CFF
KANNADA_PATTERN = re.compile(r'[\u0C80-\u0CFF]')

# In-memory storage for user language preferences (phone_number -> language)
# In production, use Redis or database
USER_LANGUAGE_PREFS: Dict[str, str] = {}

def set_user_language(phone_number: str, language: str):
    """Store user's language preference."""
    USER_LANGUAGE_PREFS[phone_number] = language

def get_user_language(phone_number: str) -> str:
    """Get user's stored language preference, defaults to 'en'."""
    return USER_LANGUAGE_PREFS.get(phone_number, 'en')

def detect_language(text: str) -> str:
    """
    Detect if text contains Kannada characters.
    Returns 'kn' for Kannada, 'en' for English.
    """
    if KANNADA_PATTERN.search(text):
        return 'kn'
    return 'en'

# Translation dictionary
TRANSLATIONS = {
    'en': {
        'welcome': """👋 *Welcome to MediChain AI!*

I'm your medical assistant. I can:

📸 *Analyze Reports*
Send a photo/PDF of your medical report for instant AI analysis

💬 *Answer Questions*
Ask me anything medical:
  • "What does high CRP mean?"
  • "Explain cholesterol levels"
  • "What causes diabetes?"
  • "How to lower blood pressure?"

🔬 *AI-Powered*
  ✓ Medical knowledge base
  ✓ Conversational memory
  ✓ Evidence-based answers

🌐 *Language*
  • Type "Kannada" or "ಕನ್ನಡ" to switch to Kannada
  • Type "English" to switch back

Try asking me a question!""",
        
        'processing': "⏳ Analyzing your report with 3-layer AI pipeline...\n\nThis will take 1-5 seconds.",
        'reset_confirm': "🔄 Conversation reset! How can I help you today?",
        'analysis_complete': "✅ *Analysis Complete*",
        'report_type': "📋 *Report Type*",
        'ai_analysis': "🔍 *AI Analysis*",
        'abnormal_findings': "⚠️ *Abnormal Findings*",
        'key_values': "📊 *Key Values*",
        'health_concerns': "🔍 *Possible Health Concerns*",
        'good_news': "✅ *Good News*: No significant abnormalities detected in the analyzed values.",
        'urgency': "Urgency",
        'risk_indicators': "📈 *Risk Indicators*",
        'suggested_consultation': "👨‍⚕️ *Suggested Consultation*",
        'important_disclaimer': "⚠️ *Important*: This is an AI screening tool trained on diabetes/heart/kidney datasets. Results are for reference only. Always consult a qualified doctor for accurate diagnosis.",
        'ai_pipeline': "🤖 *AI Pipeline Used*",
        'privacy_note': "🔒 *Privacy*: Your report was deleted from our servers immediately after analysis.",
        'view_full': "🌐 View full analysis: https://medichain.app/patient",
        'error_message': """❌ *Analysis Failed*

We encountered an issue processing your report. This could be due to:

• Image quality (try a clearer photo)
• Network connectivity
• Temporary service issue

Please try again or visit our web dashboard:
🌐 https://medichain.app/patient

Need help? Contact support@medichain.app""",
        'tip': "💡 *Tip*: Send a photo/PDF of your medical report for detailed analysis!",
        'urgency_low': "Routine follow-up recommended",
        'urgency_medium': "Schedule appointment within 1-2 weeks",
        'urgency_high': "Seek medical attention within 48-72 hours",
        'urgency_critical': "Seek immediate medical attention",
    },
    'kn': {
        'welcome': """👋 *ಮೆಡಿಚೈನ್ AI ಗೆ ಸ್ವಾಗತ!*

ನಾನು ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ಸಹಾಯಕ. ನಾನು ಮಾಡಬಲ್ಲೆ:

📸 *ವರದಿಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಿ*
ತ್ವರಿತ AI ವಿಶ್ಲೇಷಣೆಗಾಗಿ ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ವರದಿಯ ಫೋಟೋ/PDF ಕಳುಹಿಸಿ

💬 *ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ*
ವೈದ್ಯಕೀಯ ಬಗ್ಗೆ ಏನು ಬೇಕಾದರೂ ಕೇಳಿ:
  • "ಹೆಚ್ಚಿನ CRP ಎಂದರೇನು?"
  • "ಕೊಲೆಸ್ಟ್ರಾಲ್ ಮಟ್ಟಗಳನ್ನು ವಿವರಿಸಿ"
  • "ಮಧುಮೇಹಕ್ಕೆ ಕಾರಣವೇನು?"
  • "ರಕ್ತದೊತ್ತಡ ಕಡಿಮೆ ಮಾಡುವುದು ಹೇಗೆ?"

🔬 *AI-ಚಾಲಿತ*
  ✓ ವೈದ್ಯಕೀಯ ಜ್ಞಾನ ಬೇಸ್
  ✓ ಸಂಭಾಷಣೆ ಸ್ಮರಣೆ
  ✓ ಸಾಕ್ಷ್ಯ-ಆಧಾರಿತ ಉತ್ತರಗಳು

🌐 *ಭಾಷೆ*
  • ಇಂಗ್ಲಿಷ್‌ಗೆ ಬದಲಾಯಿಸಲು "English" ಎಂದು ಟೈಪ್ ಮಾಡಿ

ನನಗೆ ಪ್ರಶ್ನೆ ಕೇಳಿ!""",
        
        'processing': "⏳ 3-ಲೇಯರ್ AI ಪೈಪ್‌ಲೈನ್‌ನೊಂದಿಗೆ ನಿಮ್ಮ ವರದಿಯನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...\n\nಇದು 1-5 ಸೆಕೆಂಡುಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ.",
        'reset_confirm': "🔄 ಸಂಭಾಷಣೆ ಮರುಹೊಂದಿಸಲಾಗಿದೆ! ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        'analysis_complete': "✅ *ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ*",
        'report_type': "📋 *ವರದಿ ಪ್ರಕಾರ*",
        'ai_analysis': "🔍 *AI ವಿಶ್ಲೇಷಣೆ*",
        'abnormal_findings': "⚠️ *ಅಸಾಮಾನ್ಯ ಸಂಶೋಧನೆಗಳು*",
        'key_values': "📊 *ಪ್ರಮುಖ ಮೌಲ್ಯಗಳು*",
        'health_concerns': "🔍 *ಸಂಭವನೀಯ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳು*",
        'good_news': "✅ *ಒಳ್ಳೆಯ ಸುದ್ದಿ*: ವಿಶ್ಲೇಷಿಸಿದ ಮೌಲ್ಯಗಳಲ್ಲಿ ಯಾವುದೇ ಗಮನಾರ್ಹ ಅಸಾಮಾನ್ಯತೆಗಳು ಪತ್ತೆಯಾಗಿಲ್ಲ.",
        'urgency': "ತುರ್ತು",
        'risk_indicators': "📈 *ಅಪಾಯ ಸೂಚಕಗಳು*",
        'suggested_consultation': "👨‍⚕️ *ಶಿಫಾರಸು ಮಾಡಿದ ಸಮಾಲೋಚನೆ*",
        'important_disclaimer': "⚠️ *ಮುಖ್ಯ*: ಇದು ಮಧುಮೇಹ/ಹೃದಯ/ಮೂತ್ರಪಿಂಡ ಡೇಟಾಸೆಟ್‌ಗಳಲ್ಲಿ ತರಬೇತಿ ಪಡೆದ AI ಸ್ಕ್ರೀನಿಂಗ್ ಸಾಧನವಾಗಿದೆ. ಫಲಿತಾಂಶಗಳು ಕೇವಲ ಉಲ್ಲೇಖಕ್ಕಾಗಿ. ನಿಖರವಾದ ರೋಗನಿರ್ಣಯಕ್ಕಾಗಿ ಯಾವಾಗಲೂ ಅರ್ಹ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        'ai_pipeline': "🤖 *ಬಳಸಿದ AI ಪೈಪ್‌ಲೈನ್*",
        'privacy_note': "🔒 *ಗೌಪ್ಯತೆ*: ವಿಶ್ಲೇಷಣೆಯ ನಂತರ ನಿಮ್ಮ ವರದಿಯನ್ನು ನಮ್ಮ ಸರ್ವರ್‌ಗಳಿಂದ ತಕ್ಷಣ ಅಳಿಸಲಾಗಿದೆ.",
        'view_full': "🌐 ಸಂಪೂರ್ಣ ವಿಶ್ಲೇಷಣೆ ನೋಡಿ: https://medichain.app/patient",
        'error_message': """❌ *ವಿಶ್ಲೇಷಣೆ ವಿಫಲವಾಗಿದೆ*

ನಿಮ್ಮ ವರದಿಯನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸುವಲ್ಲಿ ನಾವು ಸಮಸ್ಯೆಯನ್ನು ಎದುರಿಸಿದ್ದೇವೆ. ಇದು ಈ ಕಾರಣದಿಂದಾಗಿರಬಹುದು:

• ಚಿತ್ರ ಗುಣಮಟ್ಟ (ಸ್ಪಷ್ಟವಾದ ಫೋಟೋ ಪ್ರಯತ್ನಿಸಿ)
• ನೆಟ್‌ವರ್ಕ್ ಸಂಪರ್ಕ
• ತಾತ್ಕಾಲಿಕ ಸೇವಾ ಸಮಸ್ಯೆ

ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ನಮ್ಮ ವೆಬ್ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಭೇಟಿ ನೀಡಿ:
🌐 https://medichain.app/patient

ಸಹಾಯ ಬೇಕೇ? support@medichain.app ಸಂಪರ್ಕಿಸಿ""",
        'tip': "💡 *ಸಲಹೆ*: ವಿವರವಾದ ವಿಶ್ಲೇಷಣೆಗಾಗಿ ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ವರದಿಯ ಫೋಟೋ/PDF ಕಳುಹಿಸಿ!",
        'urgency_low': "ನಿಯಮಿತ ಅನುಸರಣೆ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ",
        'urgency_medium': "1-2 ವಾರಗಳಲ್ಲಿ ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ನಿಗದಿಪಡಿಸಿ",
        'urgency_high': "48-72 ಗಂಟೆಗಳಲ್ಲಿ ವೈದ್ಯಕೀಯ ಗಮನ ಪಡೆಯಿರಿ",
        'urgency_critical': "ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಗಮನ ಪಡೆಯಿರಿ",
    }
}

def get_translation(lang: str, key: str) -> str:
    """Get translation for a key in the specified language."""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))

def translate_response(text: str, target_lang: str) -> str:
    """
    Translate common response patterns to target language.
    For complex AI-generated text, this is a simple keyword replacement.
    """
    if target_lang == 'en':
        return text
    
    # Simple keyword translations for AI-generated content
    replacements = {
        'Analysis Complete': 'ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ',
        'Report Type': 'ವರದಿ ಪ್ರಕಾರ',
        'AI Analysis': 'AI ವಿಶ್ಲೇಷಣೆ',
        'Abnormal Findings': 'ಅಸಾಮಾನ್ಯ ಸಂಶೋಧನೆಗಳು',
        'Key Values': 'ಪ್ರಮುಖ ಮೌಲ್ಯಗಳು',
        'Possible Health Concerns': 'ಸಂಭವನೀಯ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳು',
        'Good News': 'ಒಳ್ಳೆಯ ಸುದ್ದಿ',
        'Urgency': 'ತುರ್ತು',
        'Risk Indicators': 'ಅಪಾಯ ಸೂಚಕಗಳು',
        'Suggested Consultation': 'ಶಿಫಾರಸು ಮಾಡಿದ ಸಮಾಲೋಚನೆ',
        'Important': 'ಮುಖ್ಯ',
        'AI Pipeline Used': 'ಬಳಸಿದ AI ಪೈಪ್‌ಲೈನ್',
        'Privacy': 'ಗೌಪ್ಯತೆ',
        'View full analysis': 'ಸಂಪೂರ್ಣ ವಿಶ್ಲೇಷಣೆ ನೋಡಿ',
        'Tip': 'ಸಲಹೆ',
    }
    
    result = text
    for en, kn in replacements.items():
        result = result.replace(en, kn)
    
    return result
