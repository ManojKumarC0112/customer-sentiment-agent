def analyze_urgency(text):
    text_lower = text.lower()
    if any(k in text_lower for k in ["urgent", "immediately", "asap", "emergency", "critical", "now"]):
        return {"label": "High", "prob": 0.92}
    elif any(k in text_lower for k in ["soon", "quickly", "please help", "important"]):
        return {"label": "Medium", "prob": 0.78}
    else:
        return {"label": "Low", "prob": 0.65}

def apply_domain_rules(text, sentiment, urgency, domain_type):
    text_lower = text.lower()
    if domain_type == "banking" and any(k in text_lower for k in ["otp", "transaction failed", "account locked", "fraud"]):
        urgency["label"] = "High"; urgency["prob"] = 0.95
    elif domain_type == "healthcare" and any(k in text_lower for k in ["pain", "emergency", "appointment", "medication"]):
        urgency["label"] = "High"; urgency["prob"] = 0.95
    elif domain_type == "ecommerce" and any(k in text_lower for k in ["refund", "delivery", "not received", "damaged"]):
        urgency["label"] = "High"; urgency["prob"] = 0.92
    
    if sentiment["label"] == "Negative" and urgency["label"] == "High":
        priority_action = "escalate-to-human"
    elif urgency["label"] == "Medium":
        priority_action = "monitor-and-review"
    else:
        priority_action = "auto-respond"
    
    return urgency, priority_action
