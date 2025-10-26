import openai
import os
from dotenv import load_dotenv

load_dotenv()


def test_single_prompt(api_key, content):
    """Test our prompt on a single piece of content"""

    client = openai.OpenAI(api_key=api_key)

    system_prompt = """You are a content moderator. Classify social media content as HARMFUL or OK.

HARMFUL = Content that:
- Promotes, normalizes, or spreads discriminatory ideas
- Makes negative generalizations about groups (race, income, gender, etc.)  
- Could encourage prejudice or harmful attitudes toward groups
- Dismisses or mocks social justice concerns
- Contains subtle prejudice or coded language

OK = Personal complaints, venting, or constructive opinions that don't promote discrimination

Examples:
HARMFUL: "Racism is at the very heart of many political beliefs"
HARMFUL: "They're just protesting because they want attention"
HARMFUL: "Those people always complain"
OK: "I had a terrible day at work"
OK: "I disagree with this policy"

Respond exactly like this:
Classification: [HARMFUL or OK]  
Confidence: [1-5]"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Text to classify: {content}"},
            ],
            max_tokens=50,
            temperature=0.1,
        )

        result = response.choices[0].message.content.strip()
        print(f"📝 Input: {content}")
        print(f"🤖 GPT Response: {result}")
        print("-" * 50)

        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# Your real examples from the data
test_examples = [
    "Because they are protesting the exorbitant price of mayonnaise.",
    "Racism is at the very heart of many political beliefs, like it or not.",
    "Theres no such thing as an adult job. A job is a job.",
    "i'm already a resident there",
]

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = input("🔑 Enter your OpenAI API key: ").strip()

print("🧪 TESTING PROMPT ON YOUR REAL DATA")
print("=" * 60)

for i, example in enumerate(test_examples, 1):
    print(f"\n🔍 TEST {i}/4")
    test_single_prompt(api_key, example)

    if i < len(test_examples):
        input("Press Enter for next example...")

print("\n✅ Test complete! How do these results look to you?")
