import pandas as pd
import openai
from openai import OpenAI
import time
from datetime import datetime

# Configure OpenAI API
client = OpenAI(api_key="OPENAI_API_KEY")

def analyze_post_content(title, content):
    """
    Analyze post content using OpenAI API to determine maliciousness.
    """
    system_prompt = """You are an internet moderator who wants to prevent malicious content from being on the internet. 
    Evaluate the provided Reddit post for relevant information about it's maliciousness/harmfulness. If the post seems to contain malicious language or content, respond with 'MALICIOUS'. Otherwise, respond with 'SAFE'.""" # change first part
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # no o3 or 4.1
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Title: {title}\nContent: {content}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in API call: {str(e)}")
        time.sleep(20)  # Back off on error
        return None

def process_reddit_data(input_file, output_file):
    """
    Process Reddit data from CSV and filter using OpenAI
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
        
        if analysis and 'MALICIOUS' in analysis.upper():
            filtered_posts.append({
                'date': row['date'],
                'title': row['title'],
                'content': row['content'],
                'url': row['url'],
                'score': row['score'],
                'ai_analysis': analysis
            })
        
        time.sleep(0.5)  # Rate limiting
    
    filtered_df = pd.DataFrame(filtered_posts)
    filtered_df.to_csv(output_file, index=False)
    
    print(f"\nAnalysis complete. Found {len(filtered_posts)} relevant posts.")
    return filtered_df

if __name__ == "__main__":
    input_file = 'skip30reddit.csv'
    output_file = 'skip30filter.csv'
    
    filtered_data = process_reddit_data(input_file, output_file)