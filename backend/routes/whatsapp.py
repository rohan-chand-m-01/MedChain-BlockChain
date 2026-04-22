import os
import logging
import base64
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import Response
from pathlib import Path
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Load from root .env file
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / '.env')

from services.nvidia_nim import get_nvidia_client
from services.clinical_bert_local import get_clinical_bert_client
from services.random_forest import get_rf_predictor
from services.biogpt_local import get_biogpt_client
from services.medgemma_vertex import get_medgemma_vertex
from services.medical_chatbot import get_medical_chatbot
from services.receptionist_bot import get_receptionist_bot
from services.ocr_extractor import get_ocr_extractor
from services.whatsapp_i18n import (
    detect_language, 
    get_translation, 
    translate_response,
    set_user_language,
    get_user_language
)
from services.hash_computer import HashComputer
from services.aes_encryptor import AESEncryptor
from services.ipfs_uploader import IPFSUploader
from services.blockchain_client import BlockchainClient
from services.insforge import db_insert

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["WhatsApp"])


def get_twilio_client():
    """Get configured Twilio client."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        raise RuntimeError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")
    
    return Client(account_sid, auth_token)


async def persist_to_blockchain(
    phone_number: str,
    report_text: str,
    risk_level: str,
    risk_score: int
) -> dict:
    """
    Persist medical report to blockchain with privacy preservation.
    
    Pipeline:
    1. Hash phone number (SHA-256) for privacy
    2. Encrypt report text (AES-256-CBC)
    3. Upload encrypted data to IPFS
    4. Compute commitment hash (Keccak-256)
    5. Store commitment hash + risk score + risk level on blockchain (via gas wallet)
    6. Insert metadata into database
    7. Delete raw report file (if exists)
    8. Construct verification URL
    
    Returns:
        dict: {
            "success": bool,
            "record_id": str | None,
            "ipfs_cid": str | None,
            "verification_url": str | None,
            "error": str | None
        }
    """
    try:
        # Step 1: Hash phone number for privacy
        phone_hash = HashComputer.sha256(phone_number)
        logger.info(f"✓ Computed phone hash: {phone_hash[:16]}...")
        
        # Step 2: Encrypt report text
        encryption_secret = os.getenv("SERVER_ENCRYPTION_SECRET")
        if not encryption_secret:
            raise ValueError("SERVER_ENCRYPTION_SECRET not configured")
        
        encryptor = AESEncryptor(encryption_secret)
        # Convert string to bytes and encrypt with phone_hash for patient-specific encryption
        report_bytes = report_text.encode('utf-8')
        encrypted_data, iv = encryptor.encrypt(report_bytes, phone_hash)
        logger.info(f"✓ Encrypted report: {len(encrypted_data)} bytes, IV: {len(iv)} bytes")
        
        # Step 3: Upload encrypted data + IV to IPFS
        pinata_api_key = os.getenv("PINATA_API_KEY")
        pinata_secret = os.getenv("PINATA_SECRET_KEY")
        
        if not pinata_api_key or not pinata_secret:
            raise ValueError("PINATA_API_KEY and PINATA_SECRET_KEY not configured")
        
        ipfs_uploader = IPFSUploader(pinata_api_key, pinata_secret)
        # Prepend IV to encrypted data (IV is needed for decryption)
        # Format: [16 bytes IV][encrypted data]
        ipfs_payload = iv + encrypted_data
        ipfs_cid = await ipfs_uploader.upload(ipfs_payload)
        logger.info(f"✓ Uploaded to IPFS: {ipfs_cid} (IV + encrypted data)")
        
        # Step 4: Compute commitment hash (keccak256(cid + score + timestamp + phone_hash))
        import time
        timestamp = int(time.time())
        
        blockchain_client = BlockchainClient(
            rpc_url=os.getenv("ETHEREUM_RPC_URL", "http://127.0.0.1:8545"),
            contract_address=os.getenv("CONTRACT_ADDRESS", ""),
            private_key=os.getenv("GAS_WALLET_PRIVATE_KEY", "")  # Use gas wallet, not deployer
        )
        
        commitment_hash = blockchain_client.compute_commitment_hash(
            ipfs_cid=ipfs_cid,
            risk_score=risk_score,
            timestamp=timestamp,
            phone_hash=phone_hash
        )
        logger.info(f"✓ Computed commitment hash: {commitment_hash}")
        
        # Step 5: Store on blockchain (using gas wallet)
        record_id = await blockchain_client.store_record(
            commitment_hash=commitment_hash,
            risk_score=risk_score,
            risk_level=risk_level.upper()
        )
        logger.info(f"✓ Stored on blockchain: {record_id}")
        
        # Step 6: Insert metadata into database
        record_data = {
            "phone_hash": phone_hash,
            "ipfs_cid": ipfs_cid,
            "commitment_hash": commitment_hash,
            "record_id": record_id,  # Store record_id instead of tx_hash
            "risk_level": risk_level,
            "risk_score": risk_score
        }
        
        await db_insert("whatsapp_records", record_data)
        logger.info(f"✓ Inserted record into database")
        
        # Step 7: Delete raw report file (if exists)
        # Note: In current implementation, we don't save raw files to disk
        # This step is for future-proofing if file storage is added
        
        # Step 8: Construct verification URL (using record_id)
        public_url = os.getenv("PUBLIC_WEBHOOK_URL", "https://medichain.app")
        verification_url = f"{public_url}/verify/{record_id}"
        logger.info(f"✓ Verification URL: {verification_url}")
        
        return {
            "success": True,
            "record_id": record_id,
            "ipfs_cid": ipfs_cid,
            "verification_url": verification_url,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"❌ Blockchain persistence failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "record_id": None,
            "ipfs_cid": None,
            "verification_url": None,
            "error": str(e)
        }


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(None),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None),
    MessageSid: str = Form(...)
):
    """
    Twilio WhatsApp webhook - receives report images, analyzes with 3-layer AI, and responds.
    
    Pipeline:
    1. ClinicalBERT - Medical entity extraction
    2. NVIDIA Llama 3.1 8B - Biomarker analysis
    3. Random Forest - Risk prediction (73-92% accuracy)
    
    Privacy: Deletes media from Twilio immediately after download.
    """
    logger.info(f"📱 WhatsApp message from {From}: Body='{Body}', NumMedia={NumMedia}")
    
    # Detect language from user message
    user_lang = detect_language(Body) if Body else 'en'
    logger.info(f"Detected language: {user_lang}")
    
    resp = MessagingResponse()
    msg = resp.message()
    
    # Get user's stored language preference (defaults to 'en')
    user_lang = get_user_language(From)
    logger.info(f"Stored language preference for {From}: {user_lang}")
    
    # If user sends text, detect language and update preference
    if Body and Body.strip():
        detected_lang = detect_language(Body)
        # Only update if different and not a command
        if detected_lang != user_lang and Body.strip().lower() not in ["kannada", "ಕನ್ನಡ", "english", "reset", "clear"]:
            set_user_language(From, detected_lang)
            user_lang = detected_lang
            logger.info(f"Updated language preference for {From} to {user_lang} based on text")
    
    logger.info(f"Using language: {user_lang} for {From}")
    
    # No media attached - handle as chat message
    if NumMedia == 0 or not MediaUrl0:
        # If user sent a text message, respond with chatbot
        if Body and Body.strip():
            user_message = Body.strip()
            
            # Check for language switch commands
            if user_message.lower() in ["kannada", "ಕನ್ನಡ", "switch to kannada", "ಕನ್ನಡಕ್ಕೆ ಬದಲಿಸಿ"]:
                set_user_language(From, 'kn')
                msg.body("✅ ಭಾಷೆಯನ್ನು ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ!\n\nನಿಮ್ಮ ವೈದ್ಯಕೀಯ ವರದಿಗಳು ಈಗ ಕನ್ನಡದಲ್ಲಿ ವಿಶ್ಲೇಷಿಸಲ್ಪಡುತ್ತವೆ.\n\n💡 ಇಂಗ್ಲಿಷ್‌ಗೆ ಹಿಂತಿರುಗಲು \"English\" ಎಂದು ಟೈಪ್ ಮಾಡಿ.")
                logger.info(f"✓ Switched {From} to Kannada")
                return Response(content=str(resp), media_type="application/xml")
            
            if user_message.lower() in ["english", "switch to english", "en"]:
                set_user_language(From, 'en')
                msg.body("✅ Language switched to English!\n\nYour medical reports will now be analyzed in English.\n\n💡 To switch back to Kannada, type \"Kannada\" or \"ಕನ್ನಡ\".")
                logger.info(f"✓ Switched {From} to English")
                return Response(content=str(resp), media_type="application/xml")
            
            # Check for reset/clear commands (support both languages)
            reset_keywords = ["reset", "clear", "restart", "new conversation", "ಮರುಹೊಂದಿಸು", "ಹೊಸ ಸಂಭಾಷಣೆ"]
            if any(keyword in user_message.lower() for keyword in reset_keywords):
                chatbot = get_medical_chatbot()
                chatbot.reset_conversation(From)
                msg.body(get_translation(user_lang, 'reset_confirm'))
                logger.info(f"✓ Reset conversation for {From}")
                return Response(content=str(resp), media_type="application/xml")
            
            # Check for reset/clear commands
            if user_message.lower() in ["reset", "clear", "restart", "new conversation", "ಮರುಹೊಂದಿಸಿ", "ಹೊಸ ಸಂಭಾಷಣೆ"]:
                chatbot = get_medical_chatbot()
                chatbot.reset_conversation(From)
                msg.body(get_translation(user_lang, 'reset_confirm'))
                logger.info(f"✓ Reset conversation for {From}")
                return Response(content=str(resp), media_type="application/xml")
            
            # Check for common greetings (first message)
            user_lower = user_message.lower()
            if any(word in user_lower for word in ["hi", "hello", "hey", "start", "ನಮಸ್ಕಾರ", "ಹಲೋ"]) and len(user_message) < 20:
                msg.body(get_translation(user_lang, 'welcome'))
                logger.info(f"✓ Sent welcome to {From} in {user_lang}")
            
            else:
                # Check if message is receptionist-related (booking, registration, etc.)
                receptionist_keywords = [
                    "book", "appointment", "schedule", "doctor",
                    "register", "new patient", "first time",
                    "i'm here", "arrived", "check in", "checkin",
                    "pay", "payment", "bill"
                ]
                
                is_receptionist_query = any(keyword in user_message.lower() for keyword in receptionist_keywords)
                
                if is_receptionist_query:
                    # Use AI Receptionist for booking/registration/checkin/payment
                    try:
                        receptionist = get_receptionist_bot()
                        ai_response = await receptionist.handle_message(From, user_message, language=user_lang)
                        msg.body(ai_response)
                        logger.info(f"✓ Sent receptionist response to {From} in {user_lang}")
                    except Exception as e:
                        logger.error(f"Receptionist bot error: {e}")
                        error_msg = "❌ Sorry, I'm having trouble right now. Please try again." if user_lang == 'en' else "❌ ಕ್ಷಮಿಸಿ, ನನಗೆ ಈಗ ತೊಂದರೆಯಾಗುತ್ತಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
                        msg.body(error_msg)
                else:
                    # Use medical chatbot for general medical questions
                    try:
                        chatbot = get_medical_chatbot()
                        # Pass language preference to chatbot
                        ai_response = await chatbot.chat(From, user_message, language=user_lang)
                        
                        # Format response with language-specific tip
                        tip_text = get_translation(user_lang, 'tip')
                        formatted_response = f"{ai_response}\n\n{tip_text}"
                        
                        msg.body(formatted_response)
                        logger.info(f"✓ Sent chatbot response to {From} in {user_lang}")
                        
                    except Exception as e:
                        logger.error(f"Chatbot error: {e}")
                        error_msg = "❌ Sorry, I'm having trouble right now. Please try again or send a medical report for analysis." if user_lang == 'en' else "❌ ಕ್ಷಮಿಸಿ, ನನಗೆ ಈಗ ತೊಂದರೆಯಾಗುತ್ತಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ವಿಶ್ಲೇಷಣೆಗಾಗಿ ವೈದ್ಯಕೀಯ ವರದಿ ಕಳುಹಿಸಿ."
                        msg.body(error_msg)
        
        else:
            # No text and no media - send welcome
            msg.body(get_translation(user_lang, 'welcome'))
        logger.info(f"✅ Sending welcome message to {From} in {user_lang}")
        return Response(content=str(resp), media_type="application/xml")
    
    try:
        # Send processing message in user's language
        msg.body(get_translation(user_lang, 'processing'))
        
        # Download media from Twilio
        twilio_client = get_twilio_client()
        
        # Get media (follow redirects)
        import httpx
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            media_response = await client.get(
                MediaUrl0,
                auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            )
            media_response.raise_for_status()
            media_bytes = media_response.content
        
        logger.info(f"Downloaded {len(media_bytes)} bytes, type: {MediaContentType0}")
        
        # Delete media from Twilio immediately (privacy guarantee)
        try:
            message = twilio_client.messages(MessageSid).fetch()
            media_list = message.media.list()
            for media in media_list:
                media.delete()
            logger.info(f"✓ Deleted media from Twilio for message {MessageSid}")
        except Exception as e:
            logger.warning(f"Failed to delete Twilio media: {e}")
        
        # Medical AI Analysis - Use MedGemma multimodal for ALL images
        # MedGemma can analyze any medical image: lab reports, X-rays, CT scans, MRI, etc.
        # No OCR needed - multimodal analysis handles images directly
        nim_result = None
        analysis_method = "unknown"
        
        # Handle PDFs separately (still need OCR for PDFs)
        if MediaContentType0 and 'pdf' in MediaContentType0.lower():
            logger.info("PDF detected - using OCR + text analysis pipeline")
            
            # Extract text using OCR
            ocr_extractor = get_ocr_extractor(use_google_vision=False)
            ocr_text = ocr_extractor.extract_from_pdf(media_bytes)
            logger.info(f"✓ Extracted {len(ocr_text)} chars from PDF")
            
            # Fallback if extraction failed
            if not ocr_text or len(ocr_text.strip()) < 20:
                logger.warning("OCR extraction yielded minimal text")
                ocr_text = "[Medical report - text extraction yielded minimal content. Please ensure PDF is clear.]"
            
            # Try MedGemma text analysis
            try:
                medgemma_client = get_medgemma_vertex()
                if medgemma_client.is_available():
                    nim_result = await medgemma_client.analyze_report(ocr_text)
                    analysis_method = "MedGemma 27B (Vertex AI - Text)"
                    logger.info("✓ Using MedGemma 27B for PDF text analysis")
            except Exception as e:
                logger.warning(f"MedGemma text analysis failed: {e}")
        
        else:
            # ALL images (JPEG, PNG, etc.) - Use MedGemma multimodal directly (no OCR)
            # MedGemma automatically understands any medical image type
            logger.info("Image detected - using MedGemma multimodal analysis (no OCR)")
            
            try:
                medgemma_client = get_medgemma_vertex()
                if medgemma_client.is_available():
                    nim_result = await medgemma_client.analyze_xray_image(media_bytes)
                    analysis_method = "MedGemma 27B (Vertex AI - Multimodal)"
                    logger.info("✓ Using MedGemma 27B multimodal for image analysis")
            except Exception as e:
                logger.warning(f"MedGemma multimodal analysis failed: {e}")
        
        # Fallback to BioGPT or NVIDIA if MedGemma failed
        if not nim_result:
            logger.warning("MedGemma failed - falling back to OCR + text analysis")
            
            # Extract text using OCR as fallback
            ocr_extractor = get_ocr_extractor(use_google_vision=False)
            if MediaContentType0 and 'pdf' in MediaContentType0.lower():
                ocr_text = ocr_extractor.extract_from_pdf(media_bytes)
            else:
                ocr_text = ocr_extractor.extract_from_image(media_bytes)
            
            logger.info(f"✓ OCR fallback extracted {len(ocr_text)} chars")
            
            # Try BioGPT (local, pattern-based)
            try:
                biogpt_client = get_biogpt_client()
                nim_result = await biogpt_client.analyze_report(ocr_text)
                analysis_method = "BioGPT (Local)"
                logger.info("✓ Using BioGPT for medical analysis (local, privacy-focused)")
            except Exception as e:
                logger.warning(f"BioGPT failed: {e}")
        
        # Final fallback to NVIDIA if both MedGemma and BioGPT failed
        if not nim_result:
            try:
                nvidia_client = get_nvidia_client()
                
                # Need OCR text for NVIDIA
                if 'ocr_text' not in locals():
                    ocr_extractor = get_ocr_extractor(use_google_vision=False)
                    if MediaContentType0 and 'pdf' in MediaContentType0.lower():
                        ocr_text = ocr_extractor.extract_from_pdf(media_bytes)
                    else:
                        ocr_text = ocr_extractor.extract_from_image(media_bytes)
                    logger.info(f"✓ OCR for NVIDIA extracted {len(ocr_text)} chars")
                
                # Language-specific instructions
                lang_instruction = ""
                if user_lang == 'kn':
                    lang_instruction = "\n\nIMPORTANT: Respond with 'summary' and 'explanation' fields in Kannada (ಕನ್ನಡ) language. Keep JSON structure in English but text content in Kannada."
                
                # Enhanced prompt for accurate, conservative diagnosis
                analysis_prompt = f"""You are a medical AI analyzing a lab report. Be CONSERVATIVE and EVIDENCE-BASED.

LAB REPORT:
{ocr_text[:3000]}

CRITICAL RULES:
1. ONLY mention conditions if there are ABNORMAL values that directly support them
2. If all values are NORMAL, say "No significant abnormalities detected"
3. Focus on what the ABNORMAL findings indicate, not general possibilities
4. For elevated CRP/inflammation markers → focus on infection/inflammation, NOT chronic diseases
5. Do NOT diagnose diabetes/hypertension/heart disease unless glucose/BP/cardiac markers are abnormal

ANALYZE:
1. Report type (CBC, Lipid Profile, etc.)
2. List ONLY abnormal findings with values
3. What do these abnormal findings indicate?
4. Recommended specialist based on findings
5. Urgency (low if minor, medium if concerning, high if serious, critical if life-threatening)
{lang_instruction}

Respond as JSON:
{{
  "report_type": "type",
  "abnormal_findings": [{{"name": "test", "value": "X", "normal": "Y-Z", "explanation": "indicates..."}}],
  "conditions": ["only if directly supported by abnormal values"],
  "specialist": "specialist",
  "urgency": "low/medium/high/critical",
  "summary": "brief summary of findings"
}}"""

                nim_result = await nvidia_client.analyze_report(analysis_prompt)
                analysis_method = "NVIDIA Llama 3.1 8B"
                logger.info("✓ Using NVIDIA as fallback for medical analysis")
            except Exception as e:
                logger.error(f"All AI analysis methods failed: {e}")
                raise Exception("Medical AI analysis unavailable")
        
        report_type = nim_result.get("report_type", "general")
        # Handle both lab reports (biomarkers) and imaging reports (image_type)
        image_type = nim_result.get("image_type", None)
        biomarkers = nim_result.get("biomarkers", {})
        conditions = nim_result.get("conditions", [])
        specialist = nim_result.get("specialist", "General Practitioner")
        urgency = nim_result.get("urgency", "low")  # Default to 'low' (valid: low, medium, high, critical)
        
        # Use ONLY AI-analyzed conditions
        all_conditions = conditions
        
        logger.info(f"AI Analysis: Report type={report_type}, image_type={image_type}, conditions={len(all_conditions)}, urgency={urgency}")
        
        # Layer 3: Random Forest - Optional risk scoring (only if diabetes/heart/kidney detected)
        risk_score = 50
        risk_level = "medium"
        contributors = []
        accuracy = 0.80
        
        if report_type in ["diabetes", "heart", "kidney"] and biomarkers:
            rf_predictor = get_rf_predictor()
            rf_result = rf_predictor.predict(report_type, biomarkers)
            risk_score = rf_result.get("risk_score", 50)
            risk_level = rf_result.get("risk_level", "medium")
            contributors = rf_result.get("contributors", [])
            accuracy = rf_result.get("accuracy", 0.80)
            logger.info(f"Random Forest: {risk_score}% risk ({risk_level}), accuracy={int(accuracy*100)}%")
        else:
            logger.info(f"Skipping Random Forest - report type '{report_type}' not in trained models")
        
        # Determine specialist from NVIDIA or fallback
        if not specialist or specialist == "General Practitioner":
            specialist_map = {
                "diabetes": "Endocrinologist",
                "heart": "Cardiologist", 
                "kidney": "Nephrologist",
                "general": "General Practitioner"
            }
            specialist = specialist_map.get(report_type, "General Practitioner")
        
        # Format WhatsApp response with emojis and structure (in user's language)
        risk_emoji = "🟢" if risk_level == "low" else "🟡" if risk_level == "medium" else "🔴"
        
        # Display image type if it's an imaging report (X-ray, CT, MRI)
        if image_type:
            response_text = f"""{get_translation(user_lang, 'analysis_complete')}

📊 *Image Type*: {image_type}

"""
        else:
            response_text = f"""{get_translation(user_lang, 'analysis_complete')}

{get_translation(user_lang, 'report_type')}: {report_type.title()}

"""
        
        # Add NVIDIA's summary if available
        nvidia_summary = nim_result.get("summary", "")
        if nvidia_summary:
            response_text += f"� *AI Analysis*:\n{nvidia_summary}\n\n"
        
        # Add detected abnormal findings with explanations
        abnormal_findings = nim_result.get("abnormal_findings", [])
        if abnormal_findings:
            response_text += f"{get_translation(user_lang, 'abnormal_findings')}:\n"
            for finding in abnormal_findings[:5]:
                if isinstance(finding, dict):
                    name = finding.get('name', 'Unknown')
                    value = finding.get('value', 'N/A')
                    explanation = finding.get('explanation', '')
                    response_text += f"  • {name}: {value}\n"
                    if explanation:
                        response_text += f"    ↳ {explanation}\n"
                else:
                    response_text += f"  • {finding}\n"
            response_text += "\n"
        elif biomarkers:
            response_text += f"{get_translation(user_lang, 'key_values')}:\n"
            for key, value in list(biomarkers.items())[:5]:
                response_text += f"  • {key}: {value}\n"
            response_text += "\n"
        
        # Add AI-detected conditions with context (only if abnormalities found)
        if all_conditions and abnormal_findings:
            response_text += f"{get_translation(user_lang, 'health_concerns')}:\n"
            for condition in all_conditions[:3]:
                response_text += f"  • {condition}\n"
            note_text = "Note: These are AI-detected concerns based on abnormal findings. A doctor will provide accurate diagnosis." if user_lang == 'en' else "ಸೂಚನೆ: ಇವು ಅಸಾಮಾನ್ಯ ಸಂಶೋಧನೆಗಳ ಆಧಾರದ ಮೇಲೆ AI-ಪತ್ತೆಯಾದ ಕಾಳಜಿಗಳು. ವೈದ್ಯರು ನಿಖರವಾದ ರೋಗನಿರ್ಣಯವನ್ನು ನೀಡುತ್ತಾರೆ."
            response_text += f"\n💡 {note_text}\n\n"
        elif not abnormal_findings and not all_conditions:
            response_text += f"{get_translation(user_lang, 'good_news')}\n\n"
        
        # Add urgency level
        urgency_emoji = "🟢" if urgency == "low" else "🟡" if urgency == "medium" else "🟠" if urgency == "high" else "🔴"
        urgency_text = get_translation(user_lang, f'urgency_{urgency}')
        
        response_text += f"{urgency_emoji} *{get_translation(user_lang, 'urgency')}*: {urgency_text}\n\n"
        
        # Add top contributors
        if contributors:
            response_text += "� *Risk Indicators* (for {report_type} screening):\n"
            for c in contributors[:3]:
                response_text += f"  • {c['feature']}: {c.get('value', 'N/A')}\n"
            response_text += "\n"
        
        # Add specialist recommendation
        response_text += f"{get_translation(user_lang, 'suggested_consultation')}: {specialist}\n\n"
        
        # Add disclaimer
        response_text += f"{get_translation(user_lang, 'important_disclaimer')}\n\n"
        
        # Add pipeline info
        pipeline_text = "Multimodal Analysis" if "Multimodal" in analysis_method else "Text Analysis"
        response_text += f"{get_translation(user_lang, 'ai_pipeline')}:\n"
        response_text += f"  ✓ {analysis_method}\n"
        if report_type in ["diabetes", "heart", "kidney"] and biomarkers:
            response_text += f"  ✓ Random Forest ({int(accuracy*100)}% acc)\n"
        response_text += "\n"
        
        # Add privacy note
        response_text += f"{get_translation(user_lang, 'privacy_note')}\n\n"
        
        # Add web dashboard link
        response_text += f"{get_translation(user_lang, 'view_full')}"
        
        # Send follow-up message with results
        twilio_client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            body=response_text,
            to=From
        )
        
        logger.info(f"✓ Sent analysis results to {From}")
        
        # Blockchain persistence (non-blocking - errors won't affect patient analysis)
        try:
            logger.info(f"🔗 Starting blockchain persistence for {From}")
            
            # Construct full report text for encryption
            full_report = f"""Medical Report Analysis
Report Type: {report_type}
Image Type: {image_type if image_type else 'N/A'}
Risk Level: {risk_level}
Risk Score: {risk_score}%
Specialist: {specialist}
Urgency: {urgency}

AI Analysis:
{nim_result.get('summary', 'N/A')}

Conditions Detected:
{', '.join(all_conditions) if all_conditions else 'None'}

Biomarkers:
{biomarkers}
"""
            
            # Persist to blockchain
            persistence_result = await persist_to_blockchain(
                phone_number=From,
                report_text=full_report,
                risk_level=risk_level,
                risk_score=risk_score
            )
            
            if persistence_result["success"]:
                logger.info(f"✅ Blockchain persistence successful: {persistence_result['record_id']}")
                
                # Send verification URL to patient
                verification_msg = f"""🔐 *Blockchain Verification*

Your medical report has been securely stored on the blockchain.

Verification URL:
{persistence_result['verification_url']}

Share this link with insurance providers or healthcare institutions to verify the authenticity of your report.

Record ID: {persistence_result['record_id'][:16]}...
IPFS CID: {persistence_result['ipfs_cid'][:16]}...

🔒 Your data is encrypted and privacy-preserved."""
                
                # Send verification URL as separate message
                twilio_client.messages.create(
                    from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
                    body=verification_msg,
                    to=From
                )
                
                logger.info(f"✓ Sent verification URL to {From}")
            else:
                logger.warning(f"⚠️ Blockchain persistence failed (non-blocking): {persistence_result['error']}")
                
        except Exception as persistence_error:
            # Log error but don't block patient analysis
            logger.error(f"❌ Blockchain persistence error (non-blocking): {persistence_error}")
            import traceback
            traceback.print_exc()
        
        # Return empty response (already sent via Twilio API)
        return Response(content="", media_type="text/plain")
        
    except Exception as e:
        logger.error(f"WhatsApp analysis error: {e}")
        import traceback
        traceback.print_exc()
        
        msg.body(get_translation(user_lang, 'error_message'))
    
    return Response(content=str(resp), media_type="application/xml")


@router.get("/whatsapp/webhook")
async def whatsapp_webhook_verify(request: Request):
    """
    Webhook verification for Meta WhatsApp Business API.
    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge.
    """
    params = request.query_params
    
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    # Verify token (set this in your .env)
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "medichain_secure_token_2026")
    
    if mode == "subscribe" and token == verify_token:
        logger.info("✓ WhatsApp webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    else:
        logger.warning(f"WhatsApp webhook verification failed: mode={mode}, token={token}")
        raise HTTPException(status_code=403, detail="Verification failed")


@router.get("/whatsapp/status")
async def whatsapp_status():
    """Check Twilio WhatsApp configuration and webhook URL."""
    try:
        client = get_twilio_client()
        # Test connection
        account = client.api.accounts(os.getenv("TWILIO_ACCOUNT_SID")).fetch()
        
        # Get public URL (you'll need to set this when deploying)
        webhook_url = os.getenv("PUBLIC_WEBHOOK_URL", "https://your-domain.com") + "/api/whatsapp/webhook"
        
        return {
            "status": "configured",
            "account_sid": account.sid,
            "webhook_url": webhook_url,
            "whatsapp_number": os.getenv("TWILIO_WHATSAPP_NUMBER"),
            "instructions": "Configure this webhook URL in Twilio Console or Meta Business Manager"
        }
    except Exception as e:
        return {
            "status": "not_configured",
            "error": str(e),
            "instructions": "Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env"
        }
