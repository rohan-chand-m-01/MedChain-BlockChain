"""
AI Receptionist Bot - Replaces clinic receptionist with WhatsApp automation
Handles: Appointment booking, registration, queue management, payments
"""
import os
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')


class ReceptionistBot:
    """
    AI Receptionist for clinic automation via WhatsApp.
    Manages multi-step conversation flows for booking, registration, etc.
    """
    
    def __init__(self):
        # In-memory conversation state (phone_number -> state)
        # In production, use Redis or database
        self.conversation_states: Dict[str, Dict] = {}
        
        # Mock clinic data (replace with database queries)
        self.doctors = [
            {"id": "doc_1", "name": "Dr. Sharma", "specialty": "General Physician"},
            {"id": "doc_2", "name": "Dr. Patel", "specialty": "Cardiologist"},
            {"id": "doc_3", "name": "Dr. Kumar", "specialty": "Endocrinologist"},
        ]
        
        logger.info("✅ AI Receptionist Bot initialized")
    
    def get_state(self, phone_number: str) -> Dict:
        """Get conversation state for a phone number."""
        if phone_number not in self.conversation_states:
            self.conversation_states[phone_number] = {
                "flow": None,  # booking, registration, checkin, payment
                "step": 0,
                "data": {}
            }
        return self.conversation_states[phone_number]
    
    def reset_state(self, phone_number: str):
        """Reset conversation state."""
        if phone_number in self.conversation_states:
            del self.conversation_states[phone_number]
    
    async def handle_message(self, phone_number: str, message: str, language: str = 'en') -> str:
        """
        Main message handler - routes to appropriate flow.
        
        Args:
            phone_number: User's phone number
            message: User's message text
            language: User's preferred language (en/kn)
        
        Returns:
            Bot response message
        """
        state = self.get_state(phone_number)
        message_lower = message.lower().strip()
        
        # Check for flow triggers (keywords)
        if any(word in message_lower for word in ["book", "appointment", "schedule", "doctor"]):
            return await self.start_booking_flow(phone_number, language)
        
        elif any(word in message_lower for word in ["register", "new patient", "first time"]):
            return await self.start_registration_flow(phone_number, language)
        
        elif any(word in message_lower for word in ["i'm here", "arrived", "check in", "checkin"]):
            return await self.handle_checkin(phone_number, language)
        
        elif any(word in message_lower for word in ["pay", "payment", "bill"]):
            return await self.handle_payment_request(phone_number, language)
        
        # If in active flow, continue that flow
        elif state["flow"]:
            return await self.continue_flow(phone_number, message, language)
        
        # Default: Show menu
        else:
            return self.show_main_menu(language)
    
    def show_main_menu(self, language: str = 'en') -> str:
        """Show main menu of receptionist functions."""
        if language == 'kn':
            return """👋 *ನಮಸ್ಕಾರ! ನಾನು AI ರಿಸೆಪ್ಷನಿಸ್ಟ್*

ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?

📅 *ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕ್ ಮಾಡಿ*
"book appointment" ಎಂದು ಟೈಪ್ ಮಾಡಿ

📝 *ಹೊಸ ರೋಗಿ ನೋಂದಣಿ*
"register" ಎಂದು ಟೈಪ್ ಮಾಡಿ

🏥 *ಚೆಕ್-ಇನ್ (ನಾನು ಇಲ್ಲಿದ್ದೇನೆ)*
"I'm here" ಎಂದು ಟೈಪ್ ಮಾಡಿ

💳 *ಪಾವತಿ*
"payment" ಎಂದು ಟೈಪ್ ಮಾಡಿ

ಅಥವಾ ನನಗೆ ಏನು ಬೇಕಾದರೂ ಕೇಳಿ!"""
        
        return """👋 *Hello! I'm your AI Receptionist*

How can I help you today?

📅 *Book Appointment*
Type "book appointment"

📝 *New Patient Registration*
Type "register"

🏥 *Check-In (I'm here)*
Type "I'm here"

💳 *Payment*
Type "payment"

Or just ask me anything!"""

    
    # ==================== APPOINTMENT BOOKING FLOW ====================
    
    async def start_booking_flow(self, phone_number: str, language: str) -> str:
        """Start appointment booking conversation."""
        state = self.get_state(phone_number)
        state["flow"] = "booking"
        state["step"] = 1
        state["data"] = {}
        
        # Show available doctors
        doctors_list = "\n".join([
            f"{i+1}. {doc['name']} - {doc['specialty']}"
            for i, doc in enumerate(self.doctors)
        ])
        
        if language == 'kn':
            return f"""📅 *ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕಿಂಗ್*

ನೀವು ಯಾವ ವೈದ್ಯರನ್ನು ನೋಡಲು ಬಯಸುತ್ತೀರಿ?

{doctors_list}

ಸಂಖ್ಯೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ (1-{len(self.doctors)})"""
        
        return f"""📅 *Appointment Booking*

Which doctor would you like to see?

{doctors_list}

Type the number (1-{len(self.doctors)})"""
    
    async def continue_flow(self, phone_number: str, message: str, language: str) -> str:
        """Continue active conversation flow."""
        state = self.get_state(phone_number)
        flow = state["flow"]
        
        if flow == "booking":
            return await self.continue_booking_flow(phone_number, message, language)
        elif flow == "registration":
            return await self.continue_registration_flow(phone_number, message, language)
        else:
            return self.show_main_menu(language)
    
    async def continue_booking_flow(self, phone_number: str, message: str, language: str) -> str:
        """Continue appointment booking flow."""
        state = self.get_state(phone_number)
        step = state["step"]
        
        # Step 1: Doctor selection
        if step == 1:
            try:
                choice = int(message.strip())
                if 1 <= choice <= len(self.doctors):
                    selected_doctor = self.doctors[choice - 1]
                    state["data"]["doctor"] = selected_doctor
                    state["step"] = 2
                    
                    if language == 'kn':
                        return f"""✅ {selected_doctor['name']} ಆಯ್ಕೆ ಮಾಡಲಾಗಿದೆ

ನೀವು ಯಾವ ದಿನಾಂಕವನ್ನು ಬಯಸುತ್ತೀರಿ?

1. ಇಂದು ({datetime.now().strftime('%B %d')})
2. ನಾಳೆ ({(datetime.now() + timedelta(days=1)).strftime('%B %d')})
3. ಮರುದಿನ ({(datetime.now() + timedelta(days=2)).strftime('%B %d')})

ಅಥವಾ ದಿನಾಂಕವನ್ನು ಟೈಪ್ ಮಾಡಿ (DD/MM/YYYY)"""
                    
                    return f"""✅ Selected {selected_doctor['name']}

What date works for you?

1. Today ({datetime.now().strftime('%B %d')})
2. Tomorrow ({(datetime.now() + timedelta(days=1)).strftime('%B %d')})
3. Day after ({(datetime.now() + timedelta(days=2)).strftime('%B %d')})

Or type a date (DD/MM/YYYY)"""
                else:
                    return "Invalid choice. Please select 1-3." if language == 'en' else "ಅಮಾನ್ಯ ಆಯ್ಕೆ. ದಯವಿಟ್ಟು 1-3 ಆಯ್ಕೆಮಾಡಿ."
            except ValueError:
                return "Please enter a number (1-3)." if language == 'en' else "ದಯವಿಟ್ಟು ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ (1-3)."

        
        # Step 2: Date selection
        elif step == 2:
            selected_date = None
            
            # Handle quick options (1, 2, 3)
            if message.strip() in ["1", "2", "3"]:
                days_ahead = int(message.strip()) - 1
                selected_date = datetime.now() + timedelta(days=days_ahead)
            else:
                # Try parsing custom date
                try:
                    selected_date = datetime.strptime(message.strip(), '%d/%m/%Y')
                except ValueError:
                    return "Invalid date format. Use DD/MM/YYYY or select 1-3." if language == 'en' else "ಅಮಾನ್ಯ ದಿನಾಂಕ ಸ್ವರೂಪ. DD/MM/YYYY ಬಳಸಿ ಅಥವಾ 1-3 ಆಯ್ಕೆಮಾಡಿ."
            
            state["data"]["date"] = selected_date.strftime('%Y-%m-%d')
            state["step"] = 3
            
            # Show available time slots (mock data)
            slots = ["10:00 AM", "11:30 AM", "2:00 PM", "4:00 PM", "5:30 PM"]
            slots_list = "\n".join([f"{i+1}. {slot}" for i, slot in enumerate(slots)])
            
            if language == 'kn':
                return f"""📅 ದಿನಾಂಕ: {selected_date.strftime('%B %d, %Y')}

ಲಭ್ಯವಿರುವ ಸಮಯದ ಸ್ಲಾಟ್‌ಗಳು:

{slots_list}

ಸಂಖ್ಯೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ (1-{len(slots)})"""
            
            return f"""📅 Date: {selected_date.strftime('%B %d, %Y')}

Available time slots:

{slots_list}

Type the number (1-{len(slots)})"""
        
        # Step 3: Time slot selection
        elif step == 3:
            slots = ["10:00 AM", "11:30 AM", "2:00 PM", "4:00 PM", "5:30 PM"]
            
            try:
                choice = int(message.strip())
                if 1 <= choice <= len(slots):
                    selected_time = slots[choice - 1]
                    state["data"]["time"] = selected_time
                    state["step"] = 4
                    
                    if language == 'kn':
                        return """ಭೇಟಿಯ ಕಾರಣ ಏನು?

ಉದಾಹರಣೆ:
- ನಿಯಮಿತ ತಪಾಸಣೆ
- ಜ್ವರ ಮತ್ತು ಕೆಮ್ಮು
- ಮಧುಮೇಹ ಅನುಸರಣೆ
- ಲ್ಯಾಬ್ ವರದಿ ಚರ್ಚೆ"""
                    
                    return """What's the reason for your visit?

Examples:
- Routine checkup
- Fever and cough
- Diabetes follow-up
- Lab report discussion"""
                else:
                    return "Invalid choice. Please select 1-5." if language == 'en' else "ಅಮಾನ್ಯ ಆಯ್ಕೆ. ದಯವಿಟ್ಟು 1-5 ಆಯ್ಕೆಮಾಡಿ."
            except ValueError:
                return "Please enter a number (1-5)." if language == 'en' else "ದಯವಿಟ್ಟು ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ (1-5)."
        
        # Step 4: Reason for visit
        elif step == 4:
            state["data"]["reason"] = message.strip()
            
            # Create appointment confirmation
            doctor = state["data"]["doctor"]
            date = state["data"]["date"]
            time = state["data"]["time"]
            reason = state["data"]["reason"]
            
            # Reset state
            self.reset_state(phone_number)
            
            # TODO: Save to database
            
            if language == 'kn':
                return f"""✅ *ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ದೃಢೀಕರಿಸಲಾಗಿದೆ!*

👨‍⚕️ ವೈದ್ಯರು: {doctor['name']}
📅 ದಿನಾಂಕ: {date}
🕐 ಸಮಯ: {time}
📝 ಕಾರಣ: {reason}

🏥 ಕ್ಲಿನಿಕ್: ABC ಮೆಡಿಕಲ್ ಸೆಂಟರ್
📍 ವಿಳಾಸ: 123 MG Road, Bangalore

⏰ ದಯವಿಟ್ಟು 10 ನಿಮಿಷಗಳ ಮುಂಚೆ ಬನ್ನಿ

ನೀವು ಬಂದಾಗ "I'm here" ಎಂದು ಉತ್ತರಿಸಿ

ಮರುನಿಗದಿ/ರದ್ದುಗೊಳಿಸಲು: "cancel appointment" ಎಂದು ಟೈಪ್ ಮಾಡಿ"""
            
            return f"""✅ *Appointment Confirmed!*

👨‍⚕️ Doctor: {doctor['name']}
📅 Date: {date}
🕐 Time: {time}
📝 Reason: {reason}

🏥 Clinic: ABC Medical Center
📍 Address: 123 MG Road, Bangalore

⏰ Please arrive 10 minutes early

Reply "I'm here" when you arrive

To reschedule/cancel: Type "cancel appointment" """
        
        return "Something went wrong. Please start over." if language == 'en' else "ಏನೋ ತಪ್ಪಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ."

    
    # ==================== PATIENT REGISTRATION FLOW ====================
    
    async def start_registration_flow(self, phone_number: str, language: str) -> str:
        """Start patient registration conversation."""
        state = self.get_state(phone_number)
        state["flow"] = "registration"
        state["step"] = 1
        state["data"] = {}
        
        if language == 'kn':
            return """📝 *ಹೊಸ ರೋಗಿ ನೋಂದಣಿ*

ಸ್ವಾಗತ! ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ರಚಿಸೋಣ.

1️⃣ ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?"""
        
        return """📝 *New Patient Registration*

Welcome! Let's create your profile.

1️⃣ What's your full name?"""
    
    async def continue_registration_flow(self, phone_number: str, message: str, language: str) -> str:
        """Continue patient registration flow."""
        state = self.get_state(phone_number)
        step = state["step"]
        
        # Step 1: Full name
        if step == 1:
            state["data"]["name"] = message.strip()
            state["step"] = 2
            
            return "2️⃣ Age?" if language == 'en' else "2️⃣ ವಯಸ್ಸು?"
        
        # Step 2: Age
        elif step == 2:
            try:
                age = int(message.strip())
                if 1 <= age <= 120:
                    state["data"]["age"] = age
                    state["step"] = 3
                    
                    if language == 'kn':
                        return """3️⃣ ಲಿಂಗ?

1. ಪುರುಷ
2. ಮಹಿಳೆ
3. ಇತರೆ"""
                    
                    return """3️⃣ Gender?

1. Male
2. Female
3. Other"""
                else:
                    return "Please enter a valid age (1-120)." if language == 'en' else "ದಯವಿಟ್ಟು ಮಾನ್ಯ ವಯಸ್ಸನ್ನು ನಮೂದಿಸಿ (1-120)."
            except ValueError:
                return "Please enter a number." if language == 'en' else "ದಯವಿಟ್ಟು ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ."
        
        # Step 3: Gender
        elif step == 3:
            gender_map = {"1": "Male", "2": "Female", "3": "Other"}
            if message.strip() in gender_map:
                state["data"]["gender"] = gender_map[message.strip()]
                state["step"] = 4
                
                if language == 'kn':
                    return """4️⃣ ಯಾವುದೇ ಅಸ್ತಿತ್ವದಲ್ಲಿರುವ ವೈದ್ಯಕೀಯ ಪರಿಸ್ಥಿತಿಗಳು?

ಉದಾಹರಣೆ: ಮಧುಮೇಹ, ಅಧಿಕ ರಕ್ತದೊತ್ತಡ, ಆಸ್ತಮಾ

ಇಲ್ಲದಿದ್ದರೆ "none" ಎಂದು ಟೈಪ್ ಮಾಡಿ"""
                
                return """4️⃣ Any existing medical conditions?

Examples: Diabetes, Hypertension, Asthma

Type "none" if none"""
            else:
                return "Please select 1, 2, or 3." if language == 'en' else "ದಯವಿಟ್ಟು 1, 2, ಅಥವಾ 3 ಆಯ್ಕೆಮಾಡಿ."
        
        # Step 4: Medical conditions
        elif step == 4:
            conditions = message.strip() if message.strip().lower() != "none" else "None"
            state["data"]["conditions"] = conditions
            state["step"] = 5
            
            if language == 'kn':
                return """5️⃣ ಪ್ರಸ್ತುತ ಔಷಧಿಗಳು?

ಉದಾಹರಣೆ: Metformin 500mg, Aspirin

ಇಲ್ಲದಿದ್ದರೆ "none" ಎಂದು ಟೈಪ್ ಮಾಡಿ"""
            
            return """5️⃣ Current medications?

Examples: Metformin 500mg, Aspirin

Type "none" if none"""
        
        # Step 5: Medications
        elif step == 5:
            medications = message.strip() if message.strip().lower() != "none" else "None"
            state["data"]["medications"] = medications
            
            # Registration complete
            name = state["data"]["name"]
            age = state["data"]["age"]
            gender = state["data"]["gender"]
            conditions = state["data"]["conditions"]
            
            # Reset state
            self.reset_state(phone_number)
            
            # TODO: Save to database
            
            if language == 'kn':
                return f"""✅ *ನೋಂದಣಿ ಪೂರ್ಣಗೊಂಡಿದೆ!*

📋 ಪ್ರೊಫೈಲ್ ಸಾರಾಂಶ:
👤 ಹೆಸರು: {name}
🎂 ವಯಸ್ಸು: {age}
⚧ ಲಿಂಗ: {gender}
🏥 ಪರಿಸ್ಥಿತಿಗಳು: {conditions}
💊 ಔಷಧಿಗಳು: {medications}

ನೀವು ಈಗ ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್‌ಗಳನ್ನು ಬುಕ್ ಮಾಡಬಹುದು!

"book appointment" ಎಂದು ಟೈಪ್ ಮಾಡಿ"""
            
            return f"""✅ *Registration Complete!*

📋 Profile Summary:
👤 Name: {name}
🎂 Age: {age}
⚧ Gender: {gender}
🏥 Conditions: {conditions}
💊 Medications: {medications}

You can now book appointments!

Type "book appointment" to get started"""
        
        return "Something went wrong. Please start over." if language == 'en' else "ಏನೋ ತಪ್ಪಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ."

    
    # ==================== CHECK-IN / QUEUE MANAGEMENT ====================
    
    async def handle_checkin(self, phone_number: str, language: str) -> str:
        """Handle patient check-in when they arrive at clinic."""
        # TODO: Query database for today's appointment
        # Mock data for now
        has_appointment = True
        
        if not has_appointment:
            if language == 'kn':
                return """❌ ಇಂದು ನಿಮಗೆ ಯಾವುದೇ ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಕಂಡುಬಂದಿಲ್ಲ.

ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕ್ ಮಾಡಲು "book appointment" ಎಂದು ಟೈಪ್ ಮಾಡಿ"""
            
            return """❌ No appointment found for you today.

Type "book appointment" to schedule one"""
        
        # Mock queue data
        queue_position = 3
        estimated_wait = 15
        current_patient = 2
        
        if language == 'kn':
            return f"""✅ *ಚೆಕ್-ಇನ್ ಯಶಸ್ವಿಯಾಗಿದೆ!*

📍 ಸ್ಥಾನ: #{queue_position} ಸರದಿಯಲ್ಲಿ
⏱️ ಅಂದಾಜು ಕಾಯುವಿಕೆ: {estimated_wait} ನಿಮಿಷಗಳು

👨‍⚕️ Dr. Sharma ಪ್ರಸ್ತುತ ರೋಗಿ #{current_patient} ಜೊತೆ ಇದ್ದಾರೆ

🔔 ನಿಮ್ಮ ಸರದಿ ಬಂದಾಗ ನಾವು ನಿಮಗೆ ತಿಳಿಸುತ್ತೇವೆ

💺 ದಯವಿಟ್ಟು ಕಾಯುವ ಪ್ರದೇಶದಲ್ಲಿ ಆರಾಮವಾಗಿ ಕುಳಿತುಕೊಳ್ಳಿ"""
        
        return f"""✅ *Checked In Successfully!*

📍 Position: #{queue_position} in queue
⏱️ Estimated Wait: {estimated_wait} minutes

👨‍⚕️ Dr. Sharma is currently with Patient #{current_patient}

🔔 We'll notify you when it's your turn

💺 Please have a seat in the waiting area"""
    
    # ==================== PAYMENT HANDLING ====================
    
    async def handle_payment_request(self, phone_number: str, language: str) -> str:
        """Handle payment request after consultation."""
        # TODO: Query database for pending bill
        # Mock data for now
        
        consultation_fee = 500
        lab_tests = 800
        total = consultation_fee + lab_tests
        
        # Generate UPI payment link
        upi_id = "clinic@upi"
        clinic_name = "ABC Medical Center"
        upi_link = f"upi://pay?pa={upi_id}&pn={clinic_name}&am={total}&tn=Consultation"
        
        if language == 'kn':
            return f"""💳 *ಬಿಲ್ ಸಾರಾಂಶ*

👨‍⚕️ ಸಮಾಲೋಚನೆ: ₹{consultation_fee}
🔬 ಲ್ಯಾಬ್ ಪರೀಕ್ಷೆಗಳು: ₹{lab_tests}
━━━━━━━━━━━━━━━
💰 ಒಟ್ಟು: ₹{total}

📱 *UPI ಮೂಲಕ ಪಾವತಿಸಿ:*
{upi_link}

ಅಥವಾ QR ಕೋಡ್ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ ↓

[QR Code would be generated here]

✅ ಪಾವತಿಯ ನಂತರ, ನಿಮ್ಮ ರಸೀದಿ ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಕಳುಹಿಸಲಾಗುತ್ತದೆ"""
        
        return f"""💳 *Bill Summary*

👨‍⚕️ Consultation: ₹{consultation_fee}
🔬 Lab Tests: ₹{lab_tests}
━━━━━━━━━━━━━━━
💰 Total: ₹{total}

📱 *Pay via UPI:*
{upi_link}

Or scan QR code ↓

[QR Code would be generated here]

✅ After payment, your receipt will be sent automatically"""


# Global instance
_receptionist_bot = None


def get_receptionist_bot() -> ReceptionistBot:
    """Get or create the global receptionist bot instance."""
    global _receptionist_bot
    if _receptionist_bot is None:
        _receptionist_bot = ReceptionistBot()
    return _receptionist_bot
