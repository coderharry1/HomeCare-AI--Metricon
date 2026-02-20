import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from agents.orchestrator import run_pipeline

def analyse_chat(chat_input):
    if not chat_input.strip():
        return "⚠️ Please enter a chat message.", "", ""

    result = run_pipeline(chat_input)

    formal = result["formal_resolution"].replace(" ---", "").strip()

    sentiment = result["sentiment"]
    tone = sentiment["tone"]
    confidence = sentiment["confidence"]
    urgency = sentiment["urgency"]
    risk = sentiment["risk"]
    indicators = ", ".join(sentiment["emotional_indicators"])

    if "Frustrated" in tone or "Negative" in tone:
        tone_emoji = "🔴"
    elif "Neutral" in tone or "Moderate" in tone:
        tone_emoji = "🟡"
    else:
        tone_emoji = "🟢"

    sentiment_output = f"""{tone_emoji} Tone:               {tone}
📊 Confidence:          {confidence}
⚡ Urgency Level:       {urgency}
⚠️  Satisfaction Risk:  {risk}
💬 Emotional Keywords:  {indicators}"""

    recommendation = result["recommendation"]
    return formal, sentiment_output, recommendation

examples = [
    ['Chat: "My ceiling has started cracking again even though it was repaired last month!!" Topic: Warranty - Repair Issue'],
    ['Chat: "I got charged twice this month, fix it ASAP please!!" Topic: Billing - Overcharge'],
    ['Chat: "Where is my order?? It was supposed to arrive yesterday!!" Topic: Delivery - Late Shipment'],
    ['Chat: "I just wanted to say your support team was amazing, thank you!" Topic: Feedback - Positive'],
    ['Chat: "My new home has water leaking through the roof, its only 3 months old!!" Topic: Warranty - Defect'],
]

css = """
body { background-color: #0f172a !important; }
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    font-family: 'Georgia', serif !important;
}
.header-box {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    border-radius: 16px;
    padding: 32px;
    text-align: center;
    margin-bottom: 24px;
    border: 1px solid #4f46e5;
}
.header-box h1 {
    color: #e0e7ff !important;
    font-size: 2.2em !important;
    margin: 0 0 8px 0 !important;
}
.header-box p {
    color: #a5b4fc !important;
    margin: 4px 0 !important;
    font-size: 14px !important;
}
.badge {
    display: inline-block;
    background: rgba(99,102,241,0.2);
    border: 1px solid #6366f1;
    border-radius: 20px;
    padding: 4px 14px;
    color: #a5b4fc;
    font-size: 12px;
    margin: 4px;
}
.section-label {
    font-size: 13px !important;
    font-weight: bold !important;
    color: #6366f1 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
textarea {
    background: #1e1b4b !important;
    border: 1px solid #4f46e5 !important;
    border-radius: 10px !important;
    color: #e0e7ff !important;
    font-size: 14px !important;
}
button.primary {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: bold !important;
    padding: 14px !important;
    cursor: pointer !important;
}
.output-formal {
    background: rgba(34,197,94,0.05) !important;
    border: 1px solid rgba(34,197,94,0.3) !important;
    border-radius: 10px !important;
    color: #bbf7d0 !important;
}
.output-sentiment {
    background: rgba(99,102,241,0.05) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #e0e7ff !important;
}
.output-rec {
    background: rgba(245,158,11,0.05) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 10px !important;
    color: #fde68a !important;
}
footer { display: none !important; }
"""

with gr.Blocks(title="🏠 HomeCare AI") as app:

    gr.HTML("""
    <div class="header-box">
        <h1>🏠 HomeCare AI</h1>
        <p style="font-size:18px; color:#c7d2fe; margin-bottom:8px;">
            From Complaint to Resolution in Seconds
        </p>
        <p style="color:#a5b4fc;">
            Intelligent Support Co-Pilot for Home Building Teams
        </p>
        <br/>
        <span class="badge">🏠 HomeCare AI</span>
        <span class="badge">🤖 Flan-T5-Base</span>
        <span class="badge">💬 DistilBERT</span>
        <span class="badge">🆓 100% Free & Local</span>
        <span class="badge">📊 50 Training Examples</span>
    </div>
    """)

    with gr.Row():

        with gr.Column(scale=1):
            gr.HTML('<p class="section-label">💬 Customer Chat Input</p>')
            chat_input = gr.Textbox(
                label="",
                placeholder='Chat: "My ceiling is cracking again!!" Topic: Warranty - Repair Issue',
                lines=6
            )

            analyse_btn = gr.Button(
                "🏠 Analyse Chat",
                variant="primary",
                size="lg"
            )

            gr.HTML('<p class="section-label" style="margin-top:16px">📌 Quick Examples</p>')
            gr.Examples(
                examples=examples,
                inputs=chat_input,
                label=""
            )

            gr.HTML("""
            <div style="margin-top:20px; background:rgba(30,27,75,0.6);
                        border:1px solid #4f46e5; border-radius:12px; padding:16px;">
                <p style="color:#a5b4fc; font-size:12px; margin:0 0 8px 0;
                           text-transform:uppercase; letter-spacing:0.1em;">
                    ⚙️ How It Works
                </p>
                <p style="color:#94a3b8; font-size:12px; line-height:1.6; margin:0;">
                    1️⃣ <b style="color:#e0e7ff">Sentiment Agent</b> — detects emotion & urgency<br/>
                    2️⃣ <b style="color:#e0e7ff">Formality Agent</b> — generates resolution note<br/>
                    3️⃣ <b style="color:#e0e7ff">Orchestrator</b> — combines & recommends<br/>
                    4️⃣ <b style="color:#e0e7ff">Fine-Tuned</b> — trained on 50 real scenarios
                </p>
            </div>
            """)

        with gr.Column(scale=1):
            gr.HTML('<p class="section-label">📋 Results</p>')

            formal_output = gr.Textbox(
                label="📝 Formal Resolution Note",
                lines=5,
                elem_classes="output-formal"
            )

            sentiment_output = gr.Textbox(
                label="📊 Sentiment Analysis",
                lines=7,
                elem_classes="output-sentiment"
            )

            recommendation_output = gr.Textbox(
                label="🎯 Recommendation",
                lines=2,
                elem_classes="output-rec"
            )

    analyse_btn.click(
        fn=analyse_chat,
        inputs=chat_input,
        outputs=[formal_output, sentiment_output, recommendation_output]
    )

if __name__ == "__main__":
    print("🚀 Launching HomeCare AI...")
    app.launch(css=css)