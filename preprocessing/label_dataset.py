import pandas as pd
import json
import time
import os
from tqdm import tqdm
import openai


class GPTLabeler:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

        # Our refined prompt that worked well in testing
        self.system_prompt = """You are a content moderator. 
        Classify social media content as HARMFUL or OK.

HARMFUL = Content that:
- Promotes, normalizes, or spreads discriminatory ideas
- Makes negative generalizations about groups (race, income, gender, etc.)  
- Could encourage prejudice or harmful attitudes toward groups
- Dismisses or mocks social justice concerns
- Contains subtle prejudice or coded language

OK = Personal complaints, venting, or 
constructive opinions that don't promote discrimination

Examples:
HARMFUL: "Racism is at the very heart of many political beliefs"
HARMFUL: "They're just protesting because they want attention"
HARMFUL: "Those people always complain"
OK: "I had a terrible day at work"
OK: "I disagree with this policy"

Respond exactly like this:
Classification: [HARMFUL or OK]  
Confidence: [1-5]"""

    def label_single_content(self, content):
        """Label a single piece of content using GPT-4o mini"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Text to classify: {content}"},
                ],
                max_tokens=50,
                temperature=0.1,
            )

            raw_response = response.choices[0].message.content.strip()

            # Parse the response
            classification = "UNKNOWN"
            confidence = "1"

            lines = raw_response.split("\n")
            for line in lines:
                if "Classification:" in line:
                    classification = line.split(":", 1)[1].strip()
                elif "Confidence:" in line:
                    confidence = line.split(":", 1)[1].strip()

            return {
                "classification": classification,
                "confidence": confidence,
                "raw_response": raw_response,
                "status": "success",
            }

        except Exception as e:
            return {"classification": "ERROR", "confidence": "1", "raw_response": str(e), "status": "request_error"}

    def process_batch(self, df, start_index=0, save_every=25):
        """Process the entire dataset with progress saving"""

        results = []
        progress_file = "labeling_progress.json"

        # Load existing progress if available
        if os.path.exists(progress_file) and start_index == 0:
            try:
                with open(progress_file, "r") as f:
                    existing_results = json.load(f)
                    results = existing_results
                    start_index = len(results)
                    print(f"Resuming from index {start_index}")
            except Exception as e:
                print(f"Could not load progress file: {e}")
                results = []
                start_index = 0

        print(f"Processing {len(df) - start_index} remaining samples...")
        print(f"Estimated cost: ${(len(df) - start_index) * 0.0001:.4f}")

        # Process each sample
        for idx in tqdm(range(start_index, len(df)), desc="Labeling samples"):
            row = df.iloc[idx]
            content = str(row["content"])

            # Skip very short content
            if len(content.strip()) < 5:
                label_result = {
                    "classification": "OK",
                    "confidence": "5",
                    "raw_response": "Auto-labeled: too short",
                    "status": "skipped",
                }
            else:
                label_result = self.label_single_content(content)

            # Create result record - convert numpy types to regular Python types
            result_record = {
                "index": int(idx),
                "type": str(row["type"]),
                "subreddit": str(row["subreddit"]),
                "content": str(content[:500]),  # Truncate very long content for storage
                "score": int(row["score"]) if pd.notna(row["score"]) else 0,
                "risk_score": int(row.get("risk_score", 0)),
                "gpt_classification": str(label_result["classification"]),
                "gpt_confidence": str(label_result["confidence"]),
                "gpt_raw_response": str(label_result["raw_response"]),
                "status": str(label_result["status"]),
            }

            results.append(result_record)

            # Save progress periodically
            if (idx + 1) % save_every == 0:
                with open(progress_file, "w") as f:
                    json.dump(results, f, indent=2)
                print(f"Progress saved: {len(results)} samples completed")

            # Rate limiting - be nice to OpenAI
            time.sleep(0.2)

        # Final save
        final_df = pd.DataFrame(results)
        final_df.to_csv("genz_labeled_dataset.csv", index=False)

        # Clean up progress file
        if os.path.exists(progress_file):
            os.remove(progress_file)

        return final_df

    def analyze_results(self, labeled_df):
        """Analyze the labeling results"""
        print("\n" + "=" * 60)
        print("LABELING RESULTS ANALYSIS")
        print("=" * 60)

        # Basic stats
        total_samples = len(labeled_df)
        print(f"Total samples processed: {total_samples}")

        # Classification distribution
        print(f"\nLabel Distribution:")
        label_counts = labeled_df["gpt_classification"].value_counts()
        for label, count in label_counts.items():
            percentage = (count / total_samples) * 100
            print(f"  {label}: {count:4d} ({percentage:5.1f}%)")

        # Confidence distribution
        print(f"\nConfidence Distribution:")
        conf_counts = labeled_df["gpt_confidence"].value_counts().sort_index()
        for conf, count in conf_counts.items():
            percentage = (count / total_samples) * 100
            print(f"  Confidence {conf}: {count:4d} ({percentage:5.1f}%)")

        # Risk score vs GPT labels
        if "risk_score" in labeled_df.columns:
            print(f"\nRisk Score vs GPT Labels:")
            risk_gpt_crosstab = pd.crosstab(labeled_df["risk_score"], labeled_df["gpt_classification"], margins=True)
            print(risk_gpt_crosstab)

        # Status check
        print(f"\nProcessing Status:")
        status_counts = labeled_df["status"].value_counts()
        for status, count in status_counts.items():
            print(f"  {status}: {count}")

        # Sample harmful content
        harmful_samples = labeled_df[labeled_df["gpt_classification"] == "HARMFUL"]
        if len(harmful_samples) > 0:
            print(f"\nSample HARMFUL classifications:")
            for idx, row in harmful_samples.head(3).iterrows():
                print(f"\nContent: {row['content'][:150]}...")
                print(f"Confidence: {row['gpt_confidence']}")
                print("-" * 40)


def main():
    """Run the complete labeling pipeline"""
    print("GPT-4o MINI LABELING PIPELINE")
    print("=" * 40)

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("🔑 Enter your OpenAI API key: ").strip()

    # Load sample data
    sample_file = "genz_sample_for_labeling.csv"
    try:
        df = pd.read_csv(sample_file)
        print(f"Loaded {len(df)} samples from {sample_file}")
    except FileNotFoundError:
        print(f"Could not find {sample_file}")
        print("Make sure you ran the sampling pipeline first!")
        return

    # Initialize labeler
    labeler = GPTLabeler(api_key)

    # Confirm before starting
    estimated_cost = len(df) * 0.0001
    print(f"\nAbout to process {len(df)} samples")
    print(f"Estimated time: {len(df) * 0.2 / 60:.1f} minutes")
    print(f"Estimated cost: ${estimated_cost:.4f}")

    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    # Process all samples
    print("\nStarting labeling process...")
    labeled_df = labeler.process_batch(df)

    # Analyze results
    labeler.analyze_results(labeled_df)

    print(f"\nLabeling complete!")
    print(f"Results saved to: genz_labeled_dataset.csv")
    print(f"Ready for model training!")


if __name__ == "__main__":
    main()
