import os
import json
import google.generativeai as genai

# --- Configuration ---
api_key = None
IS_CONFIGURED = False
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        IS_CONFIGURED = True
    else:
        print("WARNING: GOOGLE_API_KEY not found. AI agent will use fallback responses.")
except Exception as e:
    print(f"ERROR: Failed to configure Gemini API, will use fallback. Details: {e}")

MOCK_AI_RESPONSE = """
[Mock AI Analysis]: This feedback highlights a critical user issue requiring immediate attention. 
The user expresses significant frustration, which poses a risk to customer satisfaction. 
Recommended Action: Escalate this ticket to a senior support agent for direct follow-up within the next hour to mitigate potential churn.
"""

def get_agent_recommendation(feedback_text):
    if not IS_CONFIGURED:
        return MOCK_AI_RESPONSE
    try:
        model = genai.GenerativeModel('gemini-1.0-pro')
        prompt = f"""As an expert customer support analyst, analyze the following feedback and provide a concise, one-paragraph recommendation with an analysis and a suggested action. Feedback: "{feedback_text}" Recommendation:"""
        response = model.generate_content(prompt)
        return response.text if response.parts else MOCK_AI_RESPONSE
    except Exception as e:
        print(f"GEMINI API ERROR during generation: {e}")
        return MOCK_AI_RESPONSE

