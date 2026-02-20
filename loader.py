import pandas as pd

def load_examples(path="data/Chat Dataset.xlsx"):
    """Load training examples from Excel file"""
    df = pd.read_excel(path)
    df.columns = ["id", "input", "output"]
    df = df.dropna(subset=["input", "output"])
    return df

def get_few_shot_examples(df, n=5):
    """Return n examples as few-shot demonstrations"""
    samples = df.head(n)
    examples = []
    for _, row in samples.iterrows():
        examples.append({
            "input": str(row["input"]),
            "output": str(row["output"])
        })
    return examples

if __name__ == "__main__":
    df = load_examples()
    print(f"✅ Loaded {len(df)} examples")
    print(df.head(2))