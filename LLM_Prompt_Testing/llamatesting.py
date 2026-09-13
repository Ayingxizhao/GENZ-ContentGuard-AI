import pandas as pd
from openai import OpenAI
import time

# Configure HuggingFace client
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key="",  # replace with your HF token
)

def analyze_post_content(title, content):
    """
    Analyze post content using Llama 3.1 via HuggingFace to determine maliciousness.
    """
    system_prompt = """You are a content moderator. Classify social media content as HATE SPEECH, HARASSMENT, VIOLENT THREATS, SELF-HARM, or OK. 


HARMFUL Posts:
- Hate Speech: Content that attacks or dehumanizes groups based on characteristics (race, gender, religion, etc.); makes negative generalizations about groups; Encourages prejudice or harmful attitudes toward groups
- Harassment/Bullying: Targets or insults individuals or groups through harassment, name-calling, or humiliation
- Violent Threats and Extremism: Explicit threats of violence, encouragement of harm, or terrorist extremist content (bombings, shootings, etc)
- Self-Harm Encouragement: Promotes, glorifies, or encourages self-destructive or dangerous behavior (smoking, drinking, drugs, self-harm, suicide, etc)




OK = Content that:
- Contains personal complaints or self-directed humor
- Contains venting  
- Contains constructive criticism, disagreement, or opinions that don't promote discrimination
- Could be negative in tone, but NOT directed at anyone




Please note that the existence of sarcasm can change whether the post is malicious or not. Sarcastic content often contains a contradiction between literal words and may convey this through emphasis on words through all caps, italics, bold, or punctuation. 


However, just because the content is targeted at a group does not necessarily mean it is malicious. Some posts may target a wrong-doing group and rightfully reprimand them for their actions. A group may be targeted and constructively criticized rather than bashed or hated. Some posts may simply make observations that are not malicious about groups.


Respond exactly like this:
Classification: [HATE SPEECH, HARASSMENT, VIOLENT THREATS, SELF-HARM, or OK]  
Confidence: [1-5]"""


    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Title: {title}\nContent: {content}"}
            ],
            temperature=0.3,
            max_tokens=50,  # response only needs to be short
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in API call: {str(e)}")
        time.sleep(20)  # back off on error
        return None

def process_reddit_data(input_file, output_file):
    """
    Process Reddit data from CSV and filter using Llama 3.1
    """
    df = pd.read_csv(input_file)

    # Remove NA values
    df = df.dropna()
    print(f"After removing NA values: {len(df)} posts")

    # Apply content length filter (remove posts with content length < 10)
    df = df[df['content'].apply(lambda x: len(str(x)) >= 10)]
    print(f"After applying content length filter: {len(df)} posts")

    filtered_posts = []

    print(f"Processing {len(df)} posts...")

    for index, row in df.iterrows():
        if index % 10 == 0:
            print(f"Processed {index} posts...")

        analysis = analyze_post_content(row['title'], row['content'])

        if analysis and not 'OK' in analysis.upper():
            filtered_posts.append({
                'date': row['date'],
                'title': row['title'],
                'content': row['content'],
                'url': row['url'],
                'score': row['score'],
                'ai_analysis': analysis
            })

        time.sleep(0.5)  # rate limiting

    filtered_df = pd.DataFrame(filtered_posts)
    filtered_df.to_csv(output_file, index=False)

    print(f"\nAnalysis complete. Found {len(filtered_posts)} relevant posts.")
    return filtered_df

if __name__ == "__main__":
    input_file = '1st200.csv'
    output_file = '1st200_filtered.csv'

    filtered_data = process_reddit_data(input_file, output_file)