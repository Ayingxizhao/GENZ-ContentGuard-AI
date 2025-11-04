import openai
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


def test_single_prompt(api_key, content):
    """Test our prompt on a single piece of content"""

    client = openai.OpenAI(api_key=api_key)

    system_prompt = """You are a content moderator. Classify social media content as HARMFUL or OK. If you detect sarcasm within the post, append SARCASM to the output. (ex. HARMFUL SARCASM)


HARMFUL = Content that:
- Promotes, normalizes, or spreads discriminatory ideas
- Makes negative generalizations about groups (race, income, gender, etc.)  
- Could encourage prejudice or harmful attitudes toward groups
- Dismisses or mocks social justice concerns
- Contains subtle prejudice or coded language
- Contains threats of violence (bombings, shootings, etc)
- Promotes, glorifies, or encourages self-destructive or dangerous behavior (smoking, drinking, doing drugs, self-harm, suicide, etc)
- Targets or insults individuals or groups through harassment, name-calling, humiliation, or cyberbullying


OK = Content that:
- Contains personal complaints or self-directed humor
- Contains venting  
- Contains constructive criticism, disagreement, or opinions that don't promote discrimination
- Could be negative in tone, but NOT directed at anyone
- Contains strong opinions, as long as it is not directly hurting anyone
- Describes rough conditions and lifestyles, as long as it is not hurtfully aimed at anyone


SARCASM = Content that:
- Contains contradiction between literal words and implied meaning
- Often uses phrasing such as “sure”, “totally”, “yeah right”, “obviously”, "definitely", “of course”
- Contains context reversal / implied critique (such as praising something that is bad)
- Emphasis on verbs/adjectives through all caps, italics, or bold (words such as love, hate, amazing, horrible)
- Incorporates tone markers/emojis that may potentially indicate sarcasm (💀, 🙄, 😭, 🤡, “/s”)
- Uses excessive punctuation such as !!! and ???
- May use rhetorical questions


Examples (NO SARCASM):
HARMFUL: "Racism is at the very heart of many political beliefs"
HARMFUL: "They're just protesting because they want attention"
HARMFUL: "Those people always complain"
HARMFUL: “They’re always so dramatic about racism”
OK: "I had a terrible day at work"
OK: "I disagree with this policy"
OK: “This subreddit is so negative today”


Examples (SARCASM):
HARMFUL: “White people are totally not rude at all.”
HARMFUL: “Millennials are definitely not annoying at all!!!”
HARMFUL: “I just love how you manage to make everything about yourself!”
HARMFUL: “Oh, sure, everyone loves lazy students who just complain all the time.”
OK: “Doesn’t waiting in line all day just sound so fun???”
OK: “Of course I’d love to do my chores! 🙄”
OK: “Oh great, another Monday… just what I needed.”
OK: “Yeah, because doing my homework early is my favorite thing ever 💀”


However, please note that just because the content is targeted at a group does not necessarily mean it is malicious. Please interpret the content to determine. For example, some posts may target a wrong-doing group and rightfully reprimand them for their actions. When a group is targeted, you need to determine whether the group is rightfully or wrongfully targeted. 
For example: “Perverts are so weird. They need to get a grip.”
Another example is when a group is targeted, but the content is more similar to constructive criticism than outright bashing or hate. Please correctly interpret the tone of the content.
For example: “Gen Z can come off as a bit unaware of others’ feelings. Some of them could use a touch more courtesy.”
Also note that some posts that have mention of specific groups may just be making observations. As long as these observations are not directly malicious towards these groups of people, they are fine. For example: “Illegal immigrants, such as Mexicans, put Americans at risk of losing their jobs.” This example is not malicious because although it acknowledges a group that is affecting America, it is not directly hurting or maliciously targeting the group.




Respond exactly like this:
Classification: [HARMFUL or OK (+ optional SARCASM)]  
Confidence: [1-5] (+ optional second confidence score for sarcasm)"""


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
#test_examples = pd.read_csv("genz_sample_for_labeling.csv", nrows=500)
test_examples = pd.read_csv(r"C:\Users\janie\OneDrive\Desktop\New folder\HAI_project\LLM_Prompt_Testing\genz_sample_for_labeling.csv", nrows = 500)


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = input("🔑 Enter your OpenAI API key: ").strip()

#print("🧪 TESTING PROMPT ON YOUR REAL DATA")
#print("=" * 60)

for i, example in enumerate(test_examples["content"], 1):
    #print(f"\n🔍 TEST {i}/100")
    try:
        test_single_prompt(api_key, example)
    except Exception as e:
        print(f"⚠️ Error on test {i}: {e}")

    #if i < len(test_examples):
        #input("Press Enter for next example...")

print("\n✅ Test complete! How do these results look to you?")
