import pandas as pd

# Load the CSV with sentiment results
df = pd.read_csv("data/feedback_with_sentiment.csv", quotechar='"')

def urgency_score(feedback, sentiment):
    """
    Simple urgency scoring logic:
    - Negative sentiment gets higher urgency
    - Positive sentiment gets lower urgency
    - Confidence can slightly adjust the score
    """
    score = 0
    if sentiment == "NEGATIVE":
        score = 3
    elif sentiment == "NEUTRAL":
        score = 2
    else:  # POSITIVE
        score = 1

    # Optional: weight by confidence
    # Here, if confidence column exists
    if 'confidence' in df.columns:
        conf = df.loc[df['feedback_text'] == feedback, 'confidence'].values[0]
        score *= conf

    return round(score, 2)

# Apply urgency scoring
df['urgency'] = df.apply(lambda x: urgency_score(x['feedback_text'], x['sentiment']), axis=1)

# Save final CSV
df.to_csv("data/feedback_final.csv", index=False)

print("✅ Urgency scoring complete. Saved to data/feedback_final.csv")
print(df)
