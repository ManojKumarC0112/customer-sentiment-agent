import os
import re
import csv
import io
import json
from datetime import datetime, timedelta
from collections import Counter

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Correctly load the .env file from the project's root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from database import SessionLocal, init_db
from models import User, Feedback
from sentiment import analyze_sentiment
from ai_agent import get_agent_recommendation

# Mock functions for urgency analysis as urgency.py is not provided.
# In a real application, these would contain more sophisticated logic.
def analyze_urgency(text: str) -> dict:
    """Mock urgency analysis based on keywords."""
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in ["urgent", "asap", "immediate", "cannot work", "broken"]):
        return {"label": "High", "prob": 0.9}
    if any(keyword in text_lower for keyword in ["slow", "issue", "problem", "confusing"]):
        return {"label": "Medium", "prob": 0.6}
    return {"label": "Low", "prob": 0.2}

def apply_domain_rules(text: str, sentiment: dict, urgency: dict, domain: str) -> tuple:
    """Mock domain rule application."""
    # This could be expanded with domain-specific logic
    if urgency["label"] == "High" and sentiment["label"] == "Negative":
        return "Escalate", "Immediate Review Required"
    return "No Action", "Standard Review"

app = Flask(__name__, template_folder="templates")
CORS(app)
init_db()

def get_feedback_themes(all_feedback_texts: list) -> list:
    """Extract common themes from feedback texts using the AI agent."""
    from ai_agent import IS_CONFIGURED
    if not IS_CONFIGURED or len(all_feedback_texts) < 5: # Require a minimum amount of data
        return ["App Performance", "Login Issues", "UI Feedback", "Feature Request"]
    try:
        model = get_agent_recommendation.__globals__['genai'].GenerativeModel('gemini-1.0-pro')
        # Use a sample of feedback to avoid overly large prompts
        feedback_block = "\n".join(f"- {text}" for text in all_feedback_texts[:50])
        prompt = f"""Analyze the following customer feedback. Identify the 3-5 most common themes. Return ONLY a valid JSON array of strings. Example: ["Login Problems", "UI Suggestions", "Payment Failures"]. Feedback:\n{feedback_block}\n\nJSON Response:"""
        response = model.generate_content(prompt)
        # Clean the response to ensure it is valid JSON
        cleaned_response = re.sub(r'```json\n?|```', '', response.text.strip())
        themes = json.loads(cleaned_response)
        return themes if isinstance(themes, list) else ["AI Error: Invalid Format"]
    except Exception as e:
        print(f"GEMINI THEME EXTRACTION ERROR: {e}")
        return ["App Performance", "Login Issues", "UI Feedback"]

# --- HTML Serving Routes ---
@app.route("/")
@app.route("/login")
def login_route(): return render_template("index.html")

@app.route("/upload")
def upload_route(): return render_template("upload.html")

@app.route("/metrics")
def metrics_route(): return render_template("metrics.html")

@app.route("/about")
def about_route(): return render_template("about.html")

# --- API Routes ---
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    db: Session = SessionLocal()
    try:
        if db.query(User).filter(User.email == data.get("email")).first():
            return jsonify({"success": False, "error": "Email already registered"}), 400
        
        hashed_password = generate_password_hash(data.get("password"))
        new_user = User(
            firstName=data.get("firstName"), lastName=data.get("lastName"), 
            email=data.get("email"), password=hashed_password,
            company=data.get("company"), companyType=data.get("companyType"),
            companySize=data.get("companySize"), role=data.get("role"),
            phone=data.get("phone"), country=data.get("country")
        )
        db.add(new_user); db.commit(); db.refresh(new_user)
        user_data = {"id": new_user.id, "name": new_user.firstName, "email": new_user.email}
        return jsonify({"success": True, "user": user_data}), 201
    except Exception as e:
        db.rollback(); print(f"Signup Error: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally: db.close()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == data.get("email")).first()
        if not user or not check_password_hash(user.password, data.get("password")):
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
        user_data = {"id": user.id, "name": user.firstName, "email": user.email}
        return jsonify({"success": True, "user": user_data}), 200
    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500
    finally: db.close()

@app.route("/api/upload_csv", methods=["POST"])
def upload_csv():
    user_id = request.form.get("userId")
    if not user_id: return jsonify({"success": False, "error": "User authentication is required."}), 401
    if "file" not in request.files: return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == '': return jsonify({"success": False, "error": "No selected file"}), 400

    domain = request.form.get("domain", "general")
    db: Session = SessionLocal()
    try:
        stream = io.StringIO(file.stream.read().decode("UTF-8"))
        csv_reader = csv.DictReader(stream)
        feedback_entries = []
        for row in csv_reader:
            text = row.get('feedback') or row.get('text') or row.get('Feedback') or row.get('Text')
            if text and text.strip():
                sentiment = analyze_sentiment(text)
                urgency = analyze_urgency(text)
                _, priority_action = apply_domain_rules(text, sentiment, urgency, domain)
                feedback_entries.append(Feedback(
                    user_text=text, sentiment_label=sentiment["label"],
                    sentiment_prob=sentiment["prob"], urgency_label=urgency["label"],
                    urgency_prob=urgency["prob"], priority_action=priority_action,
                    domain=domain, user_id=user_id
                ))
        
        if feedback_entries:
            db.add_all(feedback_entries); db.commit()
        return jsonify({"success": True, "processed": len(feedback_entries)}), 200
    except UnicodeDecodeError:
        return jsonify({"success": False, "error": "Encoding error. Please save your CSV file as UTF-8."}), 400
    except Exception as e:
        db.rollback(); print(f"CSV Upload Error: {e}")
        return jsonify({"success": False, "error": "Failed to process CSV file."}), 500
    finally: db.close()

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    user_id = request.args.get('userId')
    if not user_id: return jsonify({"success": False, "error": "User ID is required."}), 401

    db: Session = SessionLocal()
    try:
        all_feedback = db.query(Feedback).filter(Feedback.user_id == user_id).order_by(Feedback.timestamp.desc()).all()
        total = len(all_feedback)
        if total == 0:
            return jsonify({"success": True, "summary": {"total": 0}, "charts": {}, "critical_feedback": [], "themes": []})

        positive_count = sum(1 for f in all_feedback if f.sentiment_label == "Positive")
        negative_count = sum(1 for f in all_feedback if f.sentiment_label == "Negative")
        high_urgency_count = sum(1 for f in all_feedback if f.urgency_label == "High")
        score_sum = sum(f.sentiment_prob if f.sentiment_label == 'Positive' else -f.sentiment_prob if f.sentiment_label == 'Negative' else 0 for f in all_feedback)
        
        critical_feedback = [
            {"id": f.id, "text": f.user_text, "timestamp": f.timestamp.strftime('%Y-%m-%d %H:%M'), 
             "priority": round(((1 - f.sentiment_prob) + f.urgency_prob) / 2 * 10)} 
            for f in all_feedback if f.sentiment_label == "Negative" and f.urgency_label == "High"
        ][:10]
        
        today = datetime.utcnow().date()
        feedback_counts_by_date = Counter(f.timestamp.date() for f in all_feedback)
        trend_data = [{"date": (today - timedelta(days=i)).strftime('%m-%d'), "count": feedback_counts_by_date.get(today - timedelta(days=i), 0)} for i in range(29, -1, -1)]

        metrics = {
            "success": True,
            "summary": {
                "total": total,
                "high_urgency": (high_urgency_count / total * 100),
                "positive": (positive_count / total * 100),
                "negative": (negative_count / total * 100),
                "avg_score": score_sum / total if total > 0 else 0
            },
            "charts": {
                "sentiment": {"Positive": positive_count, "Neutral": total - positive_count - negative_count, "Negative": negative_count},
                "urgency": {"High": high_urgency_count, "Medium": sum(1 for f in all_feedback if f.urgency_label == "Medium"), "Low": sum(1 for f in all_feedback if f.urgency_label == "Low")},
                "trend": trend_data
            },
            "critical_feedback": critical_feedback,
            "themes": get_feedback_themes([f.user_text for f in all_feedback])
        }
        return jsonify(metrics)
    except Exception as e:
        print(f"Metrics Error: {e}")
        return jsonify({"success": False, "error": "An error occurred while fetching metrics."}), 500
    finally: db.close()

@app.route("/api/agent_insight/<int:feedback_id>", methods=["GET"])
def get_insight(feedback_id):
    db: Session = SessionLocal()
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback: return jsonify({"success": False, "error": "Feedback not found"}), 404
        recommendation = get_agent_recommendation(feedback.user_text)
        return jsonify({"success": True, "insight": recommendation})
    except Exception as e:
        print(f"Agent Insight Error: {e}")
        return jsonify({"success": False, "error": "Failed to get AI insight."}), 500
    finally: db.close()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

