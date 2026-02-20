from transformers import pipeline

print("⏳ Loading sentiment model...")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("✅ Sentiment model loaded!")


def analyse_sentiment(text: str) -> dict:

    text_lower = text.lower()

    # ── Smart overrides ──
    positive_phrases = ["thank you", "amazing", "great", "wonderful",
                        "excellent", "love", "happy", "pleased", "perfect",
                        "fantastic", "awesome", "brilliant", "best"]

    neutral_phrases = ["can i", "could i", "hey can", "hey could",
                       "i need to", "i would like", "please can",
                       "is it possible", "how do i", "i wanted to",
                       "can you", "could you", "needs to go"]

    strong_negative = ["theft", "useless", "junk", "ridiculous", "worst",
                       "hate", "furious", "destroyed", "smashed", "scam",
                       "disgusting", "awful", "terrible", "never again"]

    is_positive = any(p in text_lower for p in positive_phrases)
    is_neutral = any(p in text_lower for p in neutral_phrases)
    is_strong_negative = any(p in text_lower for p in strong_negative)

    # Run model
    result = sentiment_pipeline(text[:512])[0]
    label = result["label"]
    score = result["score"]

    # ── Apply overrides ──
    if is_strong_negative:
        label = "NEGATIVE"
        score = 0.98
    elif is_positive:
        label = "POSITIVE"
        score = 0.97
    elif is_neutral:
        label = "POSITIVE"
        score = 0.72

    # ── Map to tone ──
    if label == "NEGATIVE":
        if score > 0.95:
            tone = "Highly Frustrated / Negative"
            urgency = "High"
            risk = "High"
        elif score > 0.80:
            tone = "Frustrated / Negative"
            urgency = "Moderate–High"
            risk = "Medium–High"
        else:
            tone = "Mildly Frustrated / Negative"
            urgency = "Moderate"
            risk = "Medium"
    else:
        if score > 0.95:
            tone = "Satisfied / Positive"
            urgency = "Low"
            risk = "Low"
        elif score > 0.80:
            tone = "Neutral / Calm"
            urgency = "Low"
            risk = "Low"
        else:
            tone = "Mildly Positive / Neutral"
            urgency = "Low–Moderate"
            risk = "Low–Medium"

    # ── Emotional keywords ──
    negative_words = ["annoying", "useless", "junk", "crazy", "terrible",
                      "awful", "broken", "asap", "frustrated", "ridiculous",
                      "worst", "hate", "angry", "theft", "smashed", "destroyed"]
    positive_words = ["thanks", "great", "amazing", "happy", "love",
                      "perfect", "wonderful", "pleased", "good",
                      "fantastic", "awesome", "brilliant"]

    found_keywords = [w for w in negative_words + positive_words if w in text_lower]

    return {
        "tone": tone,
        "sentiment": label,
        "confidence": f"{round(score * 100, 1)}%",
        "urgency": urgency,
        "risk": risk,
        "emotional_indicators": found_keywords if found_keywords else ["None detected"]
    }


if __name__ == "__main__":
    tests = [
        'My wifi keeps cutting out!! Super annoying, fix it ASAP!!',
        'Hey can I change my delivery address please?',
        'Just wanted to say your support team was amazing, thank you!',
        'I got charged TWICE!! This is theft fix it NOW!!'
    ]
    for test in tests:
        result = analyse_sentiment(test)
        print(f"\n📊 Input: {test}")
        print(f"   Tone: {result['tone']}")
        print(f"   Urgency: {result['urgency']}")
        print(f"   Risk: {result['risk']}")