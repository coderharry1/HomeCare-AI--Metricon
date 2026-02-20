import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sentiment_agent import analyse_sentiment
from agents.formality_agent import generate_formal_summary

def run_pipeline(chat_input: str) -> dict:
    """
    Master orchestrator — runs all agents and combines results
    """
    print(f"\n🔄 Running pipeline for: {chat_input[:60]}...")

    # Agent 1 — Sentiment Analysis
    print("  📊 Running sentiment agent...")
    sentiment = analyse_sentiment(chat_input)

    # Agent 2 — Formal Summary
    print("  📝 Running formality agent...")
    formal_summary = generate_formal_summary(chat_input)

    # Combine into final structured output
    result = {
        "original_chat": chat_input,
        "formal_resolution": formal_summary,
        "sentiment": {
            "tone": sentiment["tone"],
            "confidence": sentiment["confidence"],
            "urgency": sentiment["urgency"],
            "risk": sentiment["risk"],
            "emotional_indicators": sentiment["emotional_indicators"]
        },
        "recommendation": get_recommendation(sentiment)
    }

    return result

def get_recommendation(sentiment: dict) -> str:
    """Generate action recommendation based on sentiment"""
    urgency = sentiment["urgency"]
    risk = sentiment["risk"]

    if urgency == "High" or risk == "High":
        return "⚠️ ESCALATE IMMEDIATELY — Assign to senior support agent. Follow up within 1 hour."
    elif "Moderate" in urgency or "Medium" in risk:
        return "📋 STANDARD FOLLOW-UP — Assign to available agent. Follow up within 24 hours."
    else:
        return "✅ ROUTINE — Log and close. Send satisfaction survey."

if __name__ == "__main__":
    test = 'Chat: "My internet is down again!! Super frustrated!!" Topic: Technical Issue - Connectivity'
    result = run_pipeline(test)

    print("\n" + "="*60)
    print("📋 FINAL ORCHESTRATED OUTPUT")
    print("="*60)
    print(f"\n💬 Original Chat:\n  {result['original_chat']}")
    print(f"\n📝 Formal Resolution:\n  {result['formal_resolution']}")
    print(f"\n📊 Sentiment Analysis:")
    for k, v in result['sentiment'].items():
        print(f"   {k}: {v}")
    print(f"\n🎯 Recommendation:\n  {result['recommendation']}")
    print("\n" + "="*60)