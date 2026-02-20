import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import torch
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)
from torch.utils.data import Dataset
from utils.loader import load_examples

# ── Label mapping ──────────────────────────────────────────
def assign_label(text: str) -> int:
    """
    0 = NEGATIVE
    1 = POSITIVE
    """
    text_lower = text.lower()

    positive_words = ["thank", "amazing", "great", "wonderful",
                      "pleased", "happy", "love", "perfect",
                      "fantastic", "awesome", "brilliant", "good",
                      "can i", "could i", "hey can", "i need to",
                      "i would like", "how do i", "please"]

    negative_words = ["annoying", "useless", "junk", "crazy",
                      "asap", "frustrated", "worst", "hate",
                      "angry", "theft", "broken", "terrible",
                      "fix it", "not working", "wrong", "damaged",
                      "ridiculous", "awful", "smashed", "scam",
                      "charged twice", "never", "disgusting"]

    pos_score = sum(1 for w in positive_words if w in text_lower)
    neg_score = sum(1 for w in negative_words if w in text_lower)

    if pos_score >= neg_score:
        return 1  # POSITIVE / NEUTRAL
    else:
        return 0  # NEGATIVE

# ── Custom Dataset ─────────────────────────────────────────
class ChatDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {
            key: val[idx] for key, val in self.encodings.items()
        }
        item["labels"] = torch.tensor(self.labels[idx])
        return item

# ── Main training function ─────────────────────────────────
def train():
    print("📂 Loading dataset...")
    df = load_examples()

    texts = []
    labels = []

    for _, row in df.iterrows():
        text = str(row["input"])
        if 'Chat:' in text:
            chat_part = text.split('Topic:')[0].replace('Chat:', '').strip()
            chat_part = chat_part.strip('"').strip("'")
        else:
            chat_part = text

        label = assign_label(chat_part)
        texts.append(chat_part)
        labels.append(label)

    print(f"✅ Prepared {len(texts)} training examples")
    print(f"   Positive/Neutral: {labels.count(1)}")
    print(f"   Negative: {labels.count(0)}")

    # ── Load tokenizer and model ──
    print("\n⏳ Loading DistilBERT...")
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2
    )
    print("✅ Model loaded!")

    # ── Create dataset ──
    dataset = ChatDataset(texts, labels, tokenizer)

    # ── Training arguments ──
    training_args = TrainingArguments(
        output_dir="./fine_tuned_sentiment",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        save_strategy="epoch",
        use_cpu=True  # Fixed for newer transformers
    )

    # ── Trainer ──
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset
    )

    print("\n🚀 Starting fine-tuning on your 50 examples...")
    print("   This will take about 2-3 minutes on Mac...\n")
    trainer.train()

    # ── Save fine-tuned model ──
    print("\n💾 Saving fine-tuned model...")
    model.save_pretrained("./fine_tuned_sentiment")
    tokenizer.save_pretrained("./fine_tuned_sentiment")
    print("✅ Model saved to ./fine_tuned_sentiment/")
    print("\n🎉 Fine-tuning complete!")
    print("   Your model is now trained on your 50 customer support examples!")

if __name__ == "__main__":
    train()