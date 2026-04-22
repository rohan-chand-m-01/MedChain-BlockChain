"""
Doctor WhatsApp Notification Service
Sends instant WhatsApp notifications to doctors when patients grant them access to medical records.
"""
import os
import logging
from twilio.rest import Client
from pathlib import Path
from dotenv import load_dotenv

# Load from root .env file
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

logger = logging.getLogger(__name__)


class DoctorNotifier:
    """Send WhatsApp notifications to doctors"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio credentials not configured - doctor notifications disabled")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("✓ Doctor notifier initialized")
    
    def is_available(self) -> bool:
        """Check if notifier is configured"""
        return self.client is not None
    
    async def notify_access_granted(
        self,
        doctor_phone: str,
        patient_name: str,
        risk_score: int,
        conditions: list,
        specialist: str,
        access_hours: int,
        record_id: str = None
    ) -> bool:
        """
        Send WhatsApp notification to doctor when patient grants access.
        
        Args:
            doctor_phone: Doctor's WhatsApp number (format: whatsapp:+1234567890)
            patient_name: Patient's name
            risk_score: Risk score 0-100
            conditions: List of detected conditions
            specialist: Recommended specialist type
            access_hours: Hours until access expires
            record_id: Blockchain record ID for verification
            
        Returns:
            bool: True if notification sent successfully
        """
        if not self.is_available():
            logger.warning("Doctor notifier not configured")
            return False
        
        try:
            # Ensure phone number has whatsapp: prefix
            if not doctor_phone.startswith("whatsapp:"):
                doctor_phone = f"whatsapp:{doctor_phone}"
            
            # Determine risk emoji
            if risk_score >= 75:
                risk_emoji = "🔴"
                risk_text = "HIGH"
            elif risk_score >= 50:
                risk_emoji = "🟡"
                risk_text = "MEDIUM"
            else:
                risk_emoji = "🟢"
                risk_text = "LOW"
            
            # Format conditions
            conditions_text = ", ".join(conditions[:3]) if conditions else "No specific conditions detected"
            if len(conditions) > 3:
                conditions_text += f" (+{len(conditions) - 3} more)"
            
            # Construct message
            message = f"""🏥 *New Patient Record Shared*

Dr. {doctor_phone.split(':')[1][-10:]} — your patient has granted you access to their medical record.

👤 *Patient*: {patient_name}
{risk_emoji} *Risk Score*: {risk_score}/100 ({risk_text})
🩺 *Conditions*: {conditions_text}
👨‍⚕️ *Specialist Match*: {specialist}

⏰ *Access Expires*: {access_hours} hours

🔗 View full records: {os.getenv('PUBLIC_WEBHOOK_URL', 'https://medichain.app')}/doctor"""
            
            if record_id:
                message += f"\n🔐 Record ID: {record_id[:16]}..."
            
            message += "\n\n_Powered by MediChain AI_"
            
            # Send WhatsApp message
            self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=doctor_phone
            )
            
            logger.info(f"✓ Sent access notification to doctor {doctor_phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send doctor notification: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def notify_access_expiring(
        self,
        doctor_phone: str,
        patient_name: str,
        hours_remaining: int
    ) -> bool:
        """
        Send reminder that access is expiring soon.
        
        Args:
            doctor_phone: Doctor's WhatsApp number
            patient_name: Patient's name
            hours_remaining: Hours until expiry
            
        Returns:
            bool: True if notification sent successfully
        """
        if not self.is_available():
            return False
        
        try:
            if not doctor_phone.startswith("whatsapp:"):
                doctor_phone = f"whatsapp:{doctor_phone}"
            
            message = f"""⏰ *Access Expiring Soon*

Your access to {patient_name}'s medical records will expire in {hours_remaining} hour(s).

If you need extended access, please request the patient to grant additional time.

_Powered by MediChain AI_"""
            
            self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=doctor_phone
            )
            
            logger.info(f"✓ Sent expiry reminder to doctor {doctor_phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send expiry reminder: {e}")
            return False


def get_doctor_notifier():
    """Get doctor notifier instance"""
    return DoctorNotifier()
