import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from pathlib import Path
from dotenv import load_dotenv

# Load from root .env file
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / '.env')

from routes import analyze, chatbot, tavus, organ, records, appointments, doctor, ipfs, integrations, whatsapp, access_control, ai_intern, patient_profile, verify, doctor_actions, privy_auth, secure_records, profiles, doctor_patient_view, stellar, privacy

tags_metadata = [
    {"name": "Infrastructure",    "description": "Health checks and system status"},
    {"name": "AI Analysis",       "description": "Medical report analysis, chatbot, and organ-level AI insights"},
    {"name": "Tavus AI Doctor",   "description": "AI-generated doctor video summaries and CVI conversations"},
    {"name": "Medical Records",   "description": "Patient record CRUD, caching, and cloning"},
    {"name": "Access Control",    "description": "RBAC-based access grants between patients and doctors"},
    {"name": "Appointments",      "description": "Appointment booking, cancellation, and slot management"},
    {"name": "Doctor Dashboard",  "description": "Doctor profiles, appointments, grants, and consultation notes"},
    {"name": "IPFS",              "description": "Decentralized file storage via Pinata/IPFS"},
    {"name": "Integrations",      "description": "Google Calendar OAuth and external service proxies"},
    {"name": "WhatsApp",          "description": "WhatsApp webhook for report analysis via Twilio"},
    {"name": "Stellar Blockchain", "description": "Stellar blockchain integration for proofs and payments"},
    {"name": "Privacy (FHE + ZK)", "description": "Fully Homomorphic Encryption and Zero-Knowledge Proofs"},
]

app = FastAPI(
    title="MediChain AI Backend",
    version="1.0.0",
    description="AI-powered blockchain-secured medical record platform. Use /openapi.json for Requestly import.",
    openapi_tags=tags_metadata,
)

# --- CORS ---
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses for production-grade security."""
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (adjust for your needs)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        # Permissions policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

app.add_middleware(SecurityHeadersMiddleware)

# --- Routers ---
app.include_router(analyze.router,        prefix="/api")
app.include_router(chatbot.router,        prefix="/api")
app.include_router(tavus.router,          prefix="/api")
app.include_router(organ.router,          prefix="/api")
app.include_router(records.router,        prefix="/api")
app.include_router(appointments.router,   prefix="/api")
app.include_router(doctor.router,         prefix="/api")
app.include_router(ipfs.router,           prefix="/api")
app.include_router(integrations.router,   prefix="/api")
app.include_router(whatsapp.router,       prefix="/api")
app.include_router(access_control.router, prefix="/api")
app.include_router(ai_intern.router,      prefix="/api")  # AI Medical Intern
app.include_router(patient_profile.router, prefix="/api")  # Patient Profiles
app.include_router(verify.router,         prefix="/api")  # Blockchain Verification
app.include_router(doctor_actions.router, prefix="/api")  # Doctor Actions (Notifications, PDF Generation)
app.include_router(privy_auth.router,     prefix="/api")  # Privy MPC Wallet Authentication
app.include_router(secure_records.router, prefix="/api")  # Secure Records with Client-Side Encryption
app.include_router(profiles.router,       prefix="/api")  # Profile Management (Patient & Doctor)
# app.include_router(doctor_patient_view.router, prefix="/api")  # Doctor Patient View (Comprehensive) - Temporarily disabled
app.include_router(stellar.router,        prefix="/api")  # Stellar Blockchain Integration
app.include_router(privacy.router,        prefix="/api", tags=["Privacy (FHE + ZK)"])  # Privacy: FHE + ZK-Proofs


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "MediChain AI Backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
