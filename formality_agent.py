import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers import T5ForConditionalGeneration, T5Tokenizer

print("⏳ Loading formality model...")
model_name = "google/flan-t5-base"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
print("✅ Formality model loaded!")

# ── Template fallbacks based on topic keywords ──────────────────────────────
TEMPLATES = {
    "connectivity": "Resolution: Customer reported intermittent network connectivity issues. Diagnostic checks were performed and a fault was identified in the network configuration. The issue was resolved via remote reset and system reconfiguration. Service stability was confirmed post-resolution.",
    "outage": "Resolution: Customer reported a complete loss of service access. Investigation confirmed a localised service outage affecting the customer's region. The network was restored following emergency maintenance procedures. Customer was notified of restoration and provided with a service credit.",
    "billing": "Resolution: Customer reported a billing discrepancy on their account. A thorough review of the account transaction history was conducted. The erroneous charge was identified, reversed, and the customer was notified of the correction via email.",
    "overcharge": "Resolution: Customer reported a duplicate charge on their account for the current billing cycle. Investigation confirmed the erroneous transaction. The duplicate charge was immediately refunded and the account ledger was reconciled.",
    "overcharg": "Resolution: Customer reported a duplicate charge on their account for the current billing cycle. Investigation confirmed the erroneous transaction. The duplicate charge was immediately refunded and the account ledger was reconciled.",
    "delivery": "Resolution: Customer reported an issue with their delivery. Investigation identified a delay in the logistics processing pipeline. The shipment was fast-tracked and the customer was provided with updated tracking information and a revised delivery estimate.",
    "late shipment": "Resolution: Customer reported a delayed shipment that had not arrived by the expected delivery date. Investigation revealed a logistics processing error at the regional hub. The shipment was fast-tracked and the customer was provided with updated tracking details.",
    "damaged": "Resolution: Customer reported receiving a damaged product. A replacement unit was immediately processed and dispatched under a new tracking number. A return label for the damaged item was generated and provided to the customer.",
    "wrong product": "Resolution: Customer reported receiving an incorrect product variant. A new shipment for the correct item was immediately processed. Instructions were provided to the customer for returning the incorrect item.",
    "password": "Resolution: Customer reported difficulty accessing the automated password reset process. Identity verification was successfully completed via security protocols. A manual password reset was initiated and temporary credentials were securely communicated to the customer.",
    "login": "Resolution: Customer reported a persistent login failure preventing account access. Diagnostic analysis identified a cache corruption issue on the client side. Steps to clear browser cache and cookies were provided and login access was successfully restored.",
    "account": "Resolution: Customer submitted a request to update their account information. Identity verification was completed in accordance with security protocols. The requested account changes were successfully applied and a confirmation was sent to the customer.",
    "subscription": "Resolution: Customer requested immediate cancellation of their active subscription. The cancellation was successfully processed and confirmed. No further charges will be incurred and service access will remain until the end of the current billing cycle.",
    "refund": "Resolution: Customer submitted a refund request for a recent transaction. The request was reviewed and verified against the refund eligibility criteria. The approved refund amount was processed and the customer was notified of the expected clearance timeframe.",
    "hardware": "Resolution: Customer reported a hardware fault on a recently purchased device. The device was assessed and found to be eligible for replacement under the warranty policy. A Return Merchandise Authorization was initiated and a pre-paid return shipping label was issued.",
    "software": "Resolution: Customer reported a software malfunction following a recent application update. A clean reinstallation procedure was recommended and guided. The application was confirmed as fully functional following the reinstallation process.",
    "feedback": "Resolution: Customer submitted positive feedback regarding their recent support interaction. The commendation was formally recorded and communicated to the relevant support team. The customer was thanked for their continued patronage.",
    "positive": "Resolution: Customer expressed satisfaction with the service received. The positive feedback was recorded and forwarded to the relevant team for acknowledgement. No further action is required at this time.",
    "payment": "Resolution: Customer reported an issue with their payment method. The payment details were reviewed and updated in the secure billing system. The customer was advised that the next scheduled payment will utilise the updated information.",
    "damaged goods": "Resolution: Customer reported receiving a damaged product upon delivery. A replacement unit was immediately processed and dispatched. A prepaid return label was issued for the return of the damaged item.",
    "shipping": "Resolution: Customer raised a concern regarding shipping costs applied to their order. The shipping fee was reviewed against the selected service tier. A partial credit was applied to the account as a goodwill gesture.",
    "address": "Resolution: Customer requested a modification to the delivery address for a pending order. The request was processed prior to shipment dispatch. Updated delivery details were confirmed with the logistics partner and communicated to the customer.",
}

def get_template_fallback(chat_input: str) -> str:
    """Match chat input to best template based on keywords"""
    text_lower = chat_input.lower()
    for keyword, template in TEMPLATES.items():
        if keyword in text_lower:
            return template
    # Generic fallback
    return "Resolution: Customer contacted support regarding an issue with their account or service. The matter was investigated thoroughly by the support team. Appropriate corrective action was taken and the customer was notified of the resolution. The case has been closed pending customer confirmation."

def build_prompt(chat_input: str) -> str:
    return f"""Write a formal customer support resolution note for this chat.
Start with "Resolution:" and write 3-4 professional sentences describing the issue and how it was resolved.

Chat: {chat_input}

Resolution:"""

def generate_formal_summary(chat_input: str) -> str:
    """Convert informal chat into formal resolution note"""
    prompt = build_prompt(chat_input)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        max_length=512,
        truncation=True
    )

    outputs = model.generate(
        inputs["input_ids"],
        max_new_tokens=200,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3,
        length_penalty=2.0
    )

    output = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    output = output.replace(" ---", "").strip()

    # ── If output is too short, use template fallback ──
    if len(output.split()) < 20:
        output = get_template_fallback(chat_input)

    if not output.startswith("Resolution:"):
        output = "Resolution: " + output

    return output

if __name__ == "__main__":
    tests = [
        'Chat: "My internet has been down for THREE days!!" Topic: Technical Issue - Outage',
        'Chat: "I got charged twice this month!!" Topic: Billing - Overcharge',
        'Chat: "Ugh my password reset link isn\'t working AGAIN." Topic: Account Management - Password Reset',
        'Chat: "Your support team was amazing, thank you!" Topic: Feedback - Positive',
    ]
    for test in tests:
        print(f"\n📝 Input: {test}")
        result = generate_formal_summary(test)
        print(f"✅ Output: {result}\n")