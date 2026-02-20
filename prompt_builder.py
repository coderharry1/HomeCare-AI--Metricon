import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.loader import load_examples, get_few_shot_examples

def build_formal_prompt(chat_input: str) -> str:
    """Build a few-shot prompt using training examples"""
    df = load_examples()
    examples = get_few_shot_examples(df, n=5)

    prompt = "Convert the following informal customer chat into a formal resolution note.\n\n"
    prompt += "Here are some examples:\n\n"

    for i, ex in enumerate(examples):
        prompt += f"Example {i+1}:\n"
        prompt += f"INPUT: {ex['input']}\n"
        prompt += f"OUTPUT: {ex['output']}\n\n"

    prompt += "---\n"
    prompt += "Now convert this one:\n\n"
    prompt += f"INPUT: {chat_input}\n"
    prompt += "OUTPUT:"

    return prompt

if __name__ == "__main__":
    test = 'Chat: "My internet is down again!!" Topic: Technical Issue - Connectivity'
    prompt = build_formal_prompt(test)
    print(prompt)
    print(f"\n✅ Prompt built successfully — {len(prompt)} characters")