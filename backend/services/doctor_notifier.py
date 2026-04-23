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

# Fixed alert number — always notified on every access grant
ALERT_NUMBER = "+917003565215"


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
        return self.client is not None

    def _format_phone(self, phone: str) -> str:
        if not phone.startswith("whatsapp:"):
            return f"whatsapp:{phone}"
        return phone

    def _send(self, to: str, body: str) -> bool:
        try:
            msg = self.client.messages.create(
                from_=self.from_number,
                body=body,
                to=self._format_phone(to),
            )
            logger.info(f"✓ WhatsApp sent to {to} | SID: {msg.sid} | Status: {msg.status}")
            return True
        except Exception as e:
            logger.error(f"✗ WhatsApp FAILED to {to}: {e}")
            return False

    def _format_duration(self, hours: int) -> str:
        if hours < 24:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        days = hours // 24
        return f"{days} day{'s' if days != 1 else ''}"

    def _clean_filename(self, file_name: str) -> str:
        """Convert filename to readable title e.g. 'blood_test_2024.pdf' → 'Blood Test 2024'"""
        name = file_name.rsplit(".", 1)[0] if "." in file_name else file_name
        return name.replace("_", " ").replace("-", " ").title()

    async def notify_doctor_access(
        self,
        doctor_phone: str,
        doctor_name: str,
        patient_name: str,
        risk_score: int,
        access_hours: int,
        record_id: str = None,
        analysis_id: str = None,
        file_name: str = "Medical Report",
        is_extension: bool = False,
    ) -> bool:
        """
        Called by access_control route when a patient grants access.
        Sends to the doctor (if they have a number) AND always to ALERT_NUMBER.
        """
        if not self.is_available():
            logger.warning("Doctor notifier not configured")
            return False

        if risk_score >= 75:
            risk_emoji, risk_text = "🔴", "High Risk"
        elif risk_score >= 50:
            risk_emoji, risk_text = "🟡", "Medium Risk"
        else:
            risk_emoji, risk_text = "🟢", "Low Risk"

        duration = self._format_duration(access_hours)
        display_file = self._clean_filename(file_name)
        action = "extended access to" if is_extension else "shared"

        try:
            # Message to the doctor
            doctor_msg = (
                f"🏥 *MediChain AI*\n\n"
                f"Dr. *{doctor_name}*, your patient *{patient_name}* has {action} "
                f"their medical file *{display_file}* with you for *{duration}*.\n\n"
                f"{risk_emoji} Risk Level: {risk_text} ({risk_score}/100)\n\n"
                f"🔗 View it on your dashboard: "
                f"{os.getenv('PUBLIC_WEBHOOK_URL', 'https://medichain.app')}/doctor\n\n"
                f"_Powered by MediChain AI_"
            )

            # Alert to the fixed number
            alert_msg = (
                f"🔔 *MediChain AI — Access Grant*\n\n"
                f"*{patient_name}* shared *{display_file}* with Dr. *{doctor_name}* "
                f"for *{duration}*.\n\n"
                f"{risk_emoji} Risk Level: {risk_text} ({risk_score}/100)\n\n"
                f"_Powered by MediChain AI_"
            )
        except Exception as fmt_err:
            logger.error(f"[NOTIFIER] Message formatting failed: {fmt_err}")
            alert_msg = f"🔔 MediChain AI — {patient_name} granted access to {doctor_name} for {duration}"
            doctor_msg = alert_msg

        # Send to doctor if they have a number
        sent = False
        if doctor_phone:
            sent = self._send(doctor_phone, doctor_msg)

        # Always send to the fixed alert number
        logger.info(f"[NOTIFIER] Sending alert to {ALERT_NUMBER}")
        alert_sent = self._send(ALERT_NUMBER, alert_msg)
        logger.info(f"[NOTIFIER] Alert send result: {alert_sent}")

        return sent

    async def notify_access_granted(
        self,
        doctor_phone: str,
        patient_name: str,
        risk_score: int,
        conditions: list,
        specialist: str,
        access_hours: int,
        record_id: str = None,
    ) -> bool:
        """Legacy alias — delegates to notify_doctor_access."""
        return await self.notify_doctor_access(
            doctor_phone=doctor_phone,
            doctor_name="Doctor",
            patient_name=patient_name,
            risk_score=risk_score,
            access_hours=access_hours,
        )

    async def notify_access_expiring(
        self,
        doctor_phone: str,
        patient_name: str,
        hours_remaining: int,
    ) -> bool:
        """Send reminder that access is expiring soon."""
        if not self.is_available():
            return False

        duration = self._format_duration(hours_remaining)
        message = (
            f"⏰ *MediChain AI — Access Expiring*\n\n"
            f"Your access to *{patient_name}*'s medical records expires in *{duration}*.\n\n"
            f"Ask the patient to extend access if needed.\n\n"
            f"_Powered by MediChain AI_"
        )

        return self._send(doctor_phone, message)


def get_doctor_notifier():
    return DoctorNotifier()
