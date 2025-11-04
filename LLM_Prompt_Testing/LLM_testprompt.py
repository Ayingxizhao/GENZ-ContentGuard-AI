import openai
import os
from dotenv import load_dotenv

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


Respond exactly like this:
Classification: [HARMFUL or OK (+ optional SARCASM)]  
Confidence: [1-5] 
Sarcasm Confidence: [1-5]

5 in confidence means you are very confident it is harmful. 1 in confidence means you are not at all confident that it is harmful.
5 in sarcasm confidence means you are very confident it is sarcastic. 1 in sarcasm confidence means you are not at all confident that it is sarcastic."""

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
        first_three_words = ' '.join(content.split()[:3])

        print(f"{first_three_words}")
        print(f"{result}")
        print("\n")


        return result

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# Your real examples from the data
test_examples = [
    "I baked cookies this weekend. They turned out delicious.",
"Oh, because lazy students are *always the best at exams* 🙄. Clearly.",
"I cleaned my room today. Looks much better now.",
"Sure, binge-drinking all night is definitely the way to success 😏. Works every time.",
"I went swimming this morning. Water was perfect.",
"Some communities are just troublemakers. They can't be helped.",
"Oh *great*, another Monday… just what I needed 🙄. Love Mondays.",
"Yeah, because doing my homework early is my *favorite* thing ever 💀. Exciting stuff.",
"Absolutely, *love it* when my alarm doesn’t go off 😏. Wonderful start.",
"People from that area are lazy. They never contribute anything useful.",
"Wow, because *all leaders* are perfect 🤡. No flaws at all.",
"I got a small victory today. Feeling proud of myself.",
"Sure, *everyone loves* surprise tasks at work 💀. Great timing.",
"Some professions clearly attract incompetent people. It's obvious when you see them.",
"Love how you manage to make *everything* about yourself 💀. Truly inspiring.",
"I played board games with family. Lots of laughs.",
"Those students are always failing. It's in their nature.",
"Oh yeah, because poor people are *so responsible* with their money 🙄. Totally makes sense.",
"People complaining about inequality are just making excuses. They need to get over it.",
"I went hiking with friends. Beautiful scenery and fresh air.",
"Of course, *everyone* loves paying bills on time 💀. Pure joy.",
"Those people are always whining about nothing. They just want attention.",
"Yeah, nothing like losing your keys for the hundredth time… iconic 😏. Love it.",
"Wow, my phone died… perfect timing 😏. Just what I needed.",
"Absolutely, *nothing like* forgetting passwords for the third time 😏. Amazing.",
"My phone battery died yesterday. It was so inconvenient.",
"Some people are just born lucky. I guess it’s nature.",
"I just *adore* stepping in puddles on the way to class 😭. Thrilling.",
"Stop pretending these social movements matter. They're a waste of time.",
"Oh, *amazing*, spilled juice on the floor 🙄. Love it.",
"I practiced guitar for an hour. Feeling more confident now.",
"People protesting are only causing chaos. They don't care about real issues.",
"Those activists are overreacting as usual. Their opinions don't count.",
"I cooked a new recipe. It turned out tasty.",
"Yeah, everyone *loves* getting spammed by bots 💀. Such a treat.",
"I had a terrible day at work. Nothing seemed to go right.",
"I cleaned my desk. Looks clean and neat.",
"Sure, I *love* doing laundry all day 💀. Thrilling experience.",
"Wow, *best day ever*… the printer jammed again 💀. Perfect timing.",
"Certain cultures are just more prone to violence. It's a fact.",
"I organized my closet. Very satisfying.",
"Just finished my homework. Finally, some peace and quiet.",
"I got up early to exercise. Feeling accomplished and ready.",
"Some groups always overreact. They take everything too seriously.",
"I painted a small canvas. Turned out great.",
"I went for a run this morning. Feeling refreshed and awake.",
"Wow, *best day ever*… locked my keys in the car 💀. Thrilling.",
"People who complain about the system are just lazy. They don't try hard enough.",
"Of course, *nothing beats* stepping on Legos 🙄. Favorite pain.",
"I helped my friend move. Felt great to be useful.",
"I disagreed with this policy. It doesn’t make sense to me.",
"Yeah, *nothing like* stepping on a rake 😭. Pure joy.",
"I spilled coffee on my shirt. Classic Monday morning.",
"I read a new book yesterday. Really enjoyed the plot.",
"Those activists are manipulating emotions. Their arguments are weak.",
"I went to the park. Enjoyed the sunshine and calm.",
"Some groups are clearly less competent than others. It's obvious in everything they do.",
"Oh wow, I *totally* needed to stub my toe today 💀. Exciting.",
"Oh, *perfect*, another rude comment online 🙄. Love it.",
"I cleaned my room today. Looks much better now.",
"I finished a challenging project. Feeling accomplished.",
"I watched a movie last night. It was surprisingly good.",
"Sure, some people just *aren’t meant* to succeed 😏. It's nature.",
"Oh, *fantastic*, another email from my boss 🙄. Just what I needed.",
"I watered the plants. They look healthier already.",
"I went for a bike ride. Really refreshing.",
"I organized my desk. Looks clean and neat.",
"Wow, I *totally* enjoy waiting in traffic 😏. My favorite part.",
"I practiced guitar for an hour. Feeling more confident now.",
"Yeah, because everyone *loves* getting spammed by bots 💀. Such a treat.",
"I just *adore* spilling coffee on myself in public 😂. Fantastic day.",
"Some communities are just troublemakers. They can't be helped.",
"Certain races are naturally inferior in academics. This explains the results.",
"Yay, another group project… my favorite 🙄. Can’t wait.",
"Wow, *best time ever* waiting at the DMV 💀. Just great.",
"I baked cookies this weekend. They turned out delicious.",
"I did some cleaning today. House looks much better.",
"I cleaned my desk. Looks clean and neat.",
"Absolutely love it when my Wi-Fi cuts out mid-game 💀. Best timing.",
"I learned a new skill today. Really proud of myself.",
"Sure, *nothing beats* stepping on Legos 🙄. Favorite pain.",
"The younger generation has no work ethic. They are spoiled and lazy.",
"I adopted a dog this week. They are adorable.",
"Of course, *everyone* loves paying bills on time 💀. Pure joy.",
"I played board games with family. Lots of laughs.",
"Wow, *best day ever*… locked my keys in the car 💀. Thrilling.",
"Wow, because *all leaders* are perfect 🤡. No flaws at all.",
"I cooked a new recipe. It turned out tasty.",
"Oh, because lazy students are *always the best at exams* 🙄. Clearly.",
"I had a small victory today. Feeling proud of myself.",

]

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = input("🔑 Enter your OpenAI API key: ").strip()

#print("🧪 TESTING PROMPT ON YOUR REAL DATA")
#print("=" * 60)

for i, example in enumerate(test_examples, 1):
    #print(f"\n🔍 TEST {i}/100")
    test_single_prompt(api_key, example)

    #if i < len(test_examples):
        #input("Press Enter for next example...")

print("\n✅ Test complete! How do these results look to you?")
