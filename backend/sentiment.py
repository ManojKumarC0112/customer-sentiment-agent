import pandas as pd
from transformers import pipeline

# Load CSV
df = pd.read_csv("data/feedback.csv", quotechar='"')  # handle commas in feedback

# Initialize sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    """Returns sentiment label and confidence score"""
    result = sentiment_analyzer(text)[0]
    return result['label'], result['score']

# Apply sentiment analysis
df['sentiment'], df['confidence'] = zip(*df['feedback_text'].apply(analyze_sentiment))

# Save results to a new CSV for urgency analysis
df.to_csv("data/feedback_with_sentiment.csv", index=False)

print("✅ Sentiment analysis complete. Saved to data/feedback_with_sentiment.csv")
print(df)
