# score/scoring.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from .models import Lead, Offer

# Load environment variables from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Rule layer constants
DECISION_MAKER_ROLES = ["head", "vp", "vice president", "director", "manager", "ceo", "founder", "chief"]
INFLUENCER_ROLES = ["engineer", "developer", "architect", "consultant", "analyst"]
ADJACENT_INDUSTRIES = ["saas", "b2b"]


# score/scoring.py

# score/scoring.py

def calculate_rule_score(lead: dict, offer: dict) -> int:
    """Calculates the rule-based score (max 50 points)."""
    score = 0
    
    # 1. Role Relevance (max 20 points)
    lead_role_lower = lead.get('role', '').lower()
    if any(keyword in lead_role_lower for keyword in DECISION_MAKER_ROLES):
        score += 20
    elif any(keyword in lead_role_lower for keyword in INFLUENCER_ROLES):
        score += 10
    
    # 2. Industry Match (max 20 points)
    lead_industry_lower = lead.get('industry', '').lower()
    
    # --- THIS IS THE CORRECTED LOGIC ---
    # Check if the lead's industry is PART OF any ideal use case for an exact match.
    if any(lead_industry_lower in use_case.lower() for use_case in offer.get('ideal_use_cases', [])):
        score += 20
    # Fallback to adjacent check if no exact match is found.
    elif "saas" in lead_industry_lower or "b2b" in lead_industry_lower:
        score += 10
        
    # 3. Data Completeness (max 10 points)
    required_fields = ["name", "role", "company", "industry", "location", "linkedin_bio"]
    if all(lead.get(field) for field in required_fields):
        score += 10
        
    return score

def get_ai_score_and_reasoning(lead: Lead, offer: Offer) -> (int, str):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analyze the following prospect's buying intent for our product.

    **Our Product/Offer:**
    - Name: {offer.name}
    - Value Propositions: {', '.join(offer.value_props)}
    - Ideal Use Cases / Target Industry: {', '.join(offer.ideal_use_cases)}

    **Prospect Details:**
    - Name: {lead.name}
    - Role: {lead.role}
    - Company: {lead.company}
    - Industry: {lead.industry}
    - LinkedIn Bio: {lead.linkedin_bio}

    **Task:**
    Your response MUST be in the following format, with no other text:
    Intent: [High/Medium/Low]
    Reasoning: [Your 1-2 sentence explanation]
    """
    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n')
        intent_str = lines[0].replace("Intent:", "").strip()
        reasoning_str = lines[1].replace("Reasoning:", "").strip()
        intent_map = {"High": 50, "Medium": 30, "Low": 10}
        return intent_map.get(intent_str, 10), reasoning_str
    except Exception as e:
        print(f"AI API error for lead {lead.name}: {e}")
        return 10, "AI analysis failed due to an API error."

def get_final_score_and_intent(lead: Lead, offer: Offer) -> dict:
    rule_score = calculate_rule_score(lead, offer)
    ai_points, reasoning = get_ai_score_and_reasoning(lead, offer)
    final_score = rule_score + ai_points

    # Determine intent label based on final score
    if final_score >= 80:
        intent = "High"
    elif final_score >= 50:
        intent = "Medium"
    else:
        intent = "Low"

    return {
        "score": final_score,
        "intent": intent,
        "reasoning": reasoning
    }