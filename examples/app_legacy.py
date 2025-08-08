# business.py
def should_refund(sentiment: str) -> bool:
    return sentiment == "negative"  # <- your rule stays the same

# app_legacy.py
from openai import OpenAI
from business import should_refund

client = OpenAI()

def handle_ticket(text: str):
    # ask model to classify
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Reply with only: positive, neutral, or negative."},
            {"role": "user", "content": f"Classify sentiment: {text}"}
        ],
        temperature=0
    )
    sentiment = resp.choices[0].message["content"].strip().lower()

    # ✅ business logic unchanged
    return {
        "sentiment": sentiment,
        "refund": should_refund(sentiment)
    } 