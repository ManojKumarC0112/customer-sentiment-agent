from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging

# --- Model Initialization ---

# This model is specifically fine-tuned for sentiment analysis on social media text.
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
LABELS = ["Negative", "Neutral", "Positive"]

# Use a global variable to cache the model and tokenizer so they are loaded only once.
tokenizer = None
model = None

def initialize_model():
    """Loads the tokenizer and model into memory. Catches potential errors."""
    global tokenizer, model
    if tokenizer is None or model is None:
        try:
            logging.info(f"Loading sentiment analysis model: {MODEL_NAME}...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            logging.info("Sentiment analysis model loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load sentiment model: {e}")
            # In a real app, you might have a fallback mechanism here.
            raise e

# --- Analysis Function ---

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of a given text string.

    Args:
        text: The input string to analyze.

    Returns:
        A dictionary containing the predicted 'label' and 'prob' (probability).
        Returns a default neutral score if the model is not loaded.
    """
    # Ensure model is loaded before first use
    initialize_model()

    if not model or not tokenizer:
        logging.warning("Sentiment model not available. Returning neutral.")
        return {"label": "Neutral", "prob": 0.5}

    try:
        # Tokenize the text and prepare it for the model
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Get model predictions
        outputs = model(**inputs)
        
        # Apply softmax to convert logits to probabilities
        scores = torch.softmax(outputs.logits, dim=1)
        
        # Get the index of the highest probability score
        max_idx = torch.argmax(scores)
        
        return {
            "label": LABELS[max_idx],
            "prob": float(scores[0][max_idx])
        }
    except Exception as e:
        logging.error(f"Error during sentiment analysis for text '{text[:50]}...': {e}")
        return {"label": "Neutral", "prob": 0.5}

# Initialize the model when the application starts
initialize_model()
