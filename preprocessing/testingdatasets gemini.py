import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Add parent directory to path to import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gemini_model import get_gemini_model

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_single_prompt(content):
    """Test our prompt on a single piece of content"""
    
    model = get_gemini_model()

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
        full_prompt = f"{system_prompt}\n\nText to classify: {content}"

        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 50
            }
        )

        # Handle blocked responses
        if not response.text:
            logging.warning("Response blocked by safety filters")
            return "ERROR: Content blocked"

        result = response.text.strip()
        return result

    except Exception as e:
        logging.error(f"Error processing content: {e}")
        return f"ERROR: {str(e)}"


def load_test_data(filename="genz_sample_for_labeling.csv", nrows=500):
    """Load test data from CSV file in data folder"""
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, "data", filename)
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    logging.info(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path, nrows=nrows)
    logging.info(f"Loaded {len(df)} rows")
    return df


def save_results(results_df, output_filename=None):
    """Save results to CSV in preprocessing folder"""
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"gemini_test_results_{timestamp}.csv"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_filename)
    
    results_df.to_csv(output_path, index=False)
    logging.info(f"Results saved to: {output_path}")
    return output_path


def run_batch_test(test_data, content_column="content"):
    """Run batch testing on dataset"""
    results = []
    total = len(test_data)
    
    logging.info(f"Starting batch test on {total} examples")
    print("🧪 TESTING PROMPT ON DATASET")
    print("=" * 60)
    
    for i, row in test_data.iterrows():
        content = row[content_column]
        
        if (i + 1) % 10 == 0:
            logging.info(f"Progress: {i + 1}/{total}")
        
        try:
            classification = test_single_prompt(content)
            results.append({
                "content": content,
                "classification": classification,
                "status": "success"
            })
        except Exception as e:
            logging.error(f"Error on row {i + 1}: {e}")
            results.append({
                "content": content,
                "classification": None,
                "status": f"error: {str(e)}"
            })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = input("🔑 Enter your Gemini API key: ").strip()
        os.environ["GEMINI_API_KEY"] = api_key
    
    try:
        # Load test data
        test_examples = load_test_data(nrows=500)
        
        # Run batch test
        results_df = run_batch_test(test_examples)
        
        # Save results
        output_path = save_results(results_df)
        
        # Print summary
        print("\n" + "=" * 60)
        print("✅ Test complete!")
        print(f"Total examples: {len(results_df)}")
        print(f"Successful: {len(results_df[results_df['status'] == 'success'])}")
        print(f"Errors: {len(results_df[results_df['status'] != 'success'])}")
        print(f"Results saved to: {output_path}")
        
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        print(f"\n❌ Error: {e}")
        print("Please ensure 'genz_sample_for_labeling.csv' exists in the data/ folder")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
