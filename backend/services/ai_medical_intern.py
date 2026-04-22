"""
AI Medical Intern Service
Provides intelligent assistance for doctors including patient briefings,
treatment suggestions, and RAG-based chat on patient files.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

# Use existing services
from services.nvidia_nim import get_nvidia_client


class MedicalInternAI:
    """AI Medical Intern - Smart assistant for doctors"""
    
    def __init__(self):
        self.nvidia_client = get_nvidia_client()
    
    async def generate_patient_briefing(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive patient briefing like a medical intern would prepare.
        
        Args:
            patient_data: {
                "patient_wallet": str,
                "analyses": List[Dict],  # All patient's medical analyses
                "appointments": List[Dict],
                "consultation_notes": List[Dict]
            }
        
        Returns:
            Structured briefing with summary, alerts, trends, recommendations
        """
        analyses = patient_data.get("analyses", [])
        if not analyses:
            return {
                "summary": "No medical records available for this patient.",
                "alerts": [],
                "trends": {},
                "recommendations": []
            }
        
        # Get latest analysis
        latest = analyses[0] if analyses else {}
        
        # Build context for AI
        context = self._build_patient_context(patient_data)
        
        prompt = f"""You are a medical intern preparing a briefing for a senior doctor.

PATIENT DATA:
{context}

Generate a comprehensive briefing in JSON format with:
1. executive_summary: One paragraph overview (2-3 sentences)
2. critical_alerts: List of urgent issues requiring immediate attention
3. key_findings: Important observations from recent records
4. trend_analysis: How patient's condition is changing
5. recommendations: Specific action items for the doctor
6. priority_score: 0-100 (higher = more urgent)

Focus on actionable insights. Be concise but thorough."""

        try:
            response = await self.nvidia_client.chat(prompt)
            
            # Parse JSON response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            briefing = json.loads(response_text)
            
            # Add metadata
            briefing["generated_at"] = datetime.utcnow().isoformat()
            briefing["patient_wallet"] = patient_data.get("patient_wallet")
            
            return briefing
            
        except Exception as e:
            # Fallback to basic briefing
            return self._generate_basic_briefing(patient_data)
    
    async def calculate_priority_score(self, patient_data: Dict[str, Any]) -> int:
        """
        Calculate patient priority score (0-100) based on multiple factors.
        Higher score = more urgent attention needed.
        """
        score = 0
        analyses = patient_data.get("analyses", [])
        
        if not analyses:
            return 0
        
        latest = analyses[0]
        
        # Risk score contribution (0-40 points)
        risk_score = latest.get("risk_score", 0)
        score += min(40, risk_score * 0.4)
        
        # Urgency level (0-30 points)
        urgency = latest.get("urgency", "low")
        urgency_points = {
            "critical": 30,
            "high": 20,
            "medium": 10,
            "low": 0
        }
        score += urgency_points.get(urgency, 0)
        
        # Recent changes (0-20 points)
        if len(analyses) > 1:
            prev_risk = analyses[1].get("risk_score", 0)
            curr_risk = risk_score
            if curr_risk > prev_risk + 10:
                score += 20  # Worsening significantly
            elif curr_risk > prev_risk:
                score += 10  # Worsening slightly
        
        # Time since last visit (0-10 points)
        appointments = patient_data.get("appointments", [])
        if appointments:
            last_appt = appointments[0]
            last_date = datetime.fromisoformat(last_appt.get("date", "2020-01-01"))
            days_since = (datetime.utcnow() - last_date).days
            if days_since > 90:
                score += 10
            elif days_since > 60:
                score += 5
        
        return min(100, int(score))
    
    async def rag_chat(self, query: str, patient_data: Dict[str, Any]) -> str:
        """
        RAG-based chat: Answer doctor's questions about specific patient
        using patient's medical records as context.
        
        Args:
            query: Doctor's question (e.g., "What's the trend in blood sugar?")
            patient_data: All patient records for context
        
        Returns:
            AI response based on patient's actual data
        """
        # Build comprehensive context from patient records
        context = self._build_detailed_patient_context(patient_data)
        
        prompt = f"""You are a medical AI assistant helping a doctor review a patient's records.

PATIENT MEDICAL RECORDS:
{context}

DOCTOR'S QUESTION:
{query}

Provide a clear, evidence-based answer using ONLY the information from the patient's records above.
If the records don't contain relevant information, say so.
Include specific values, dates, and trends when available.
Be concise but thorough."""

        try:
            response = await self.nvidia_client.chat(prompt)
            return response.strip()
        except Exception as e:
            return f"I apologize, but I encountered an error analyzing the patient records: {str(e)}"
    
    async def suggest_treatment_plan(self, diagnosis: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate evidence-based treatment plan suggestions.
        """
        prompt = f"""You are a medical AI assistant. Generate a treatment plan for:

DIAGNOSIS: {diagnosis}

PATIENT CONTEXT:
{json.dumps(patient_context, indent=2)}

Provide a structured treatment plan in JSON format with:
1. medications: List of recommended medications with dosing
2. lifestyle: Diet, exercise, monitoring recommendations
3. follow_up: When to follow up and what to check
4. red_flags: Warning signs patient should watch for
5. patient_education: Key points to explain to patient

Be evidence-based and practical."""

        try:
            response = await self.nvidia_client.chat(prompt)
            
            # Parse JSON
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(response_text)
            return plan
            
        except Exception as e:
            return {
                "error": str(e),
                "medications": [],
                "lifestyle": [],
                "follow_up": "Schedule follow-up as clinically appropriate",
                "red_flags": ["Worsening symptoms", "New concerning symptoms"],
                "patient_education": ["Discuss diagnosis and treatment options"]
            }
    
    async def analyze_document(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """
        Analyze uploaded medical document and extract key information.
        """
        prompt = f"""Analyze this medical document and extract key information.

DOCUMENT TYPE: {document_type}

DOCUMENT CONTENT:
{document_text}

Extract and return JSON with:
1. document_type: Confirmed type (lab_report, imaging, consultation, etc.)
2. date: Document date
3. critical_findings: List of abnormal or critical values
4. key_observations: Important clinical observations
5. follow_up_needed: What actions are recommended
6. summary: One-sentence summary

Be precise and focus on clinically significant information."""

        try:
            response = await self.nvidia_client.chat(prompt)
            
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(response_text)
            return analysis
            
        except Exception as e:
            return {
                "error": str(e),
                "document_type": document_type,
                "summary": "Document analysis failed"
            }
    
    def _build_patient_context(self, patient_data: Dict[str, Any]) -> str:
        """Build concise context string for AI prompts"""
        analyses = patient_data.get("analyses", [])
        appointments = patient_data.get("appointments", [])
        notes = patient_data.get("consultation_notes", [])
        
        context_parts = []
        
        # Latest analysis
        if analyses:
            latest = analyses[0]
            context_parts.append(f"Latest Analysis ({latest.get('created_at', 'N/A')}):")
            context_parts.append(f"- Risk Score: {latest.get('risk_score', 'N/A')}")
            context_parts.append(f"- Urgency: {latest.get('urgency', 'N/A')}")
            context_parts.append(f"- Conditions: {', '.join(latest.get('conditions', []))}")
            context_parts.append(f"- Summary: {latest.get('summary', 'N/A')}")
        
        # Recent appointments
        if appointments:
            context_parts.append(f"\nRecent Appointments: {len(appointments)}")
            for apt in appointments[:3]:
                context_parts.append(f"- {apt.get('date')} {apt.get('time')}: {apt.get('reason', 'N/A')}")
        
        # Recent notes
        if notes:
            context_parts.append(f"\nRecent Clinical Notes: {len(notes)}")
            for note in notes[:3]:
                context_parts.append(f"- {note.get('created_at', 'N/A')}: {note.get('note', 'N/A')[:100]}...")
        
        return "\n".join(context_parts)
    
    def _build_detailed_patient_context(self, patient_data: Dict[str, Any]) -> str:
        """Build detailed context for RAG chat"""
        analyses = patient_data.get("analyses", [])
        appointments = patient_data.get("appointments", [])
        notes = patient_data.get("consultation_notes", [])
        
        context_parts = ["=== PATIENT MEDICAL RECORDS ===\n"]
        
        # All analyses with full details
        if analyses:
            context_parts.append("MEDICAL ANALYSES:")
            for i, analysis in enumerate(analyses[:5], 1):  # Last 5 analyses
                context_parts.append(f"\n{i}. Analysis from {analysis.get('created_at', 'N/A')}")
                context_parts.append(f"   File: {analysis.get('file_name', 'N/A')}")
                context_parts.append(f"   Risk Score: {analysis.get('risk_score', 'N/A')}/100")
                context_parts.append(f"   Urgency: {analysis.get('urgency', 'N/A')}")
                context_parts.append(f"   Conditions: {', '.join(analysis.get('conditions', []))}")
                context_parts.append(f"   Specialist: {analysis.get('specialist', 'N/A')}")
                context_parts.append(f"   Summary: {analysis.get('summary', 'N/A')}")
                if analysis.get('improvement_plan'):
                    context_parts.append(f"   Recommendations: {', '.join(analysis.get('improvement_plan', []))}")
        
        # All appointments
        if appointments:
            context_parts.append("\n\nAPPOINTMENTS:")
            for apt in appointments:
                context_parts.append(f"- {apt.get('date')} {apt.get('time')}: {apt.get('reason', 'N/A')} (Status: {apt.get('status', 'N/A')})")
        
        # All consultation notes
        if notes:
            context_parts.append("\n\nCLINICAL NOTES:")
            for note in notes:
                context_parts.append(f"- {note.get('created_at', 'N/A')}: {note.get('note', 'N/A')}")
        
        return "\n".join(context_parts)
    
    def _generate_basic_briefing(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback basic briefing if AI fails"""
        analyses = patient_data.get("analyses", [])
        latest = analyses[0] if analyses else {}
        
        return {
            "executive_summary": f"Patient has {len(analyses)} medical record(s) on file. Latest risk score: {latest.get('risk_score', 'N/A')}.",
            "critical_alerts": ["Review patient records for detailed assessment"],
            "key_findings": latest.get("conditions", []),
            "trend_analysis": "Insufficient data for trend analysis",
            "recommendations": ["Review all available medical records", "Schedule follow-up if needed"],
            "priority_score": self._calculate_basic_priority(latest),
            "generated_at": datetime.utcnow().isoformat(),
            "patient_wallet": patient_data.get("patient_wallet")
        }
    
    def _calculate_basic_priority(self, latest_analysis: Dict[str, Any]) -> int:
        """Basic priority calculation"""
        risk_score = latest_analysis.get("risk_score", 0)
        urgency = latest_analysis.get("urgency", "low")
        
        base_score = risk_score * 0.5
        
        urgency_bonus = {
            "critical": 40,
            "high": 25,
            "medium": 10,
            "low": 0
        }
        
        return min(100, int(base_score + urgency_bonus.get(urgency, 0)))


# Singleton instance
_ai_intern = None

def get_ai_intern() -> MedicalInternAI:
    """Get singleton AI intern instance"""
    global _ai_intern
    if _ai_intern is None:
        _ai_intern = MedicalInternAI()
    return _ai_intern
