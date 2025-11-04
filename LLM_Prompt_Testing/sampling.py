import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple
from collections import Counter


# ============================================================================
# STEP 1: LOAD DATASET
# ============================================================================
def load_genz_dataset():
    """Load the GenZ Reddit dataset directly with pandas"""
    try:
        print("🚀 Loading GenZ Reddit dataset...")

        url = "https://huggingface.co/datasets/Ayingxizhao/genz_reddit/resolve/main/genz_reddit_posts5.csv"
        df = pd.read_csv(url)

        print(f"✅ Dataset loaded successfully!")
        print(f"📊 Shape: {df.shape} (rows, columns)")
        print(f"📋 Columns: {list(df.columns)}")
        print(f"📈 Total records: {len(df):,}")

        if "type" in df.columns:
            print(f"📝 Post types: {dict(df['type'].value_counts())}")

        return df

    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None


# ============================================================================
# STEP 2: SMART SAMPLING
# ============================================================================
class SmartSampler:
    def __init__(self):
        # Red flag keywords for potential discrimination
        self.red_flag_keywords = {
            "economic": ["poor", "rich", "wealthy", "broke", "homeless", "low income", "high income", "welfare", "foodstamps"],
            "racial": ["black", "white", "asian", "hispanic", "latino", "arab", "indian", "native", "race", "racist"],
            "gender": ["men", "women", "male", "female", "guy", "girl", "boys", "girls", "feminist", "masculine"],
            "general_hate": ["hate", "stupid", "dumb", "idiots", "losers", "trash", "garbage", "scum"],
            "targeting": ["those people", "they are", "all of them", "these people", "them all"],
        }

    def flag_potential_issues(self, text: str) -> Dict[str, any]:
        """Flag text for potential discrimination/targeting"""
        if pd.isna(text) or not text:
            return {"risk_score": 0}

        text_lower = str(text).lower()
        flags = {}

        # Check for red flag keywords by category
        for category, keywords in self.red_flag_keywords.items():
            flags[f"has_{category}"] = any(keyword in text_lower for keyword in keywords)

        # Check for targeting patterns
        targeting_patterns = [
            r"\bthose \w+",  # "those people", "those kids"
            r"\ball \w+ are",  # "all women are", "all men are"
            r"\bi hate \w+",  # "i hate women", "i hate rich"
            r"\w+ are (all|always)",  # "women are all", "poor are always"
        ]

        flags["has_targeting_pattern"] = any(re.search(pattern, text_lower) for pattern in targeting_patterns)

        # Overall risk score
        flags["risk_score"] = sum(flags.values())

        return flags

    def create_sample(self, df: pd.DataFrame, n_samples: int = 1000) -> pd.DataFrame:
        """Create a strategic sample of the dataset"""
        print(f"🎯 Creating strategic sample of {n_samples} records...")

        # Clean data
        df_clean = df.copy()
        df_clean["content"] = df_clean["content"].fillna("")

        # Remove AutoModerator and very short content
        df_clean = df_clean[df_clean["author"] != "AutoModerator"]
        df_clean = df_clean[df_clean["content"].str.len() > 20]

        print(f"📊 After cleaning: {len(df_clean):,} records")

        # Add risk flags
        flag_results = []
        for _, row in df_clean.iterrows():
            flags = self.flag_potential_issues(row["content"])
            flag_results.append(flags)

        flags_df = pd.DataFrame(flag_results)
        df_flagged = pd.concat([df_clean.reset_index(drop=True), flags_df.reset_index(drop=True)], axis=1)

        # Separate high-risk and low-risk
        high_risk = df_flagged[df_flagged["risk_score"] > 0].copy()
        low_risk = df_flagged[df_flagged["risk_score"] == 0].copy()

        print(f"🚩 High-risk samples: {len(high_risk):,}")
        print(f"✅ Low-risk samples: {len(low_risk):,}")

        # Sample strategy: 60% high-risk, 40% low-risk
        n_high_risk = min(int(n_samples * 0.6), len(high_risk))
        n_low_risk = min(n_samples - n_high_risk, len(low_risk))

        # Get samples
        high_risk_sample = high_risk.sample(n=n_high_risk, random_state=42) if n_high_risk > 0 else pd.DataFrame()
        low_risk_sample = low_risk.sample(n=n_low_risk, random_state=42) if n_low_risk > 0 else pd.DataFrame()

        # Combine and shuffle
        final_sample = pd.concat([high_risk_sample, low_risk_sample]).sample(frac=1, random_state=42).reset_index(drop=True)

        print(f"🎯 Final sample: {len(final_sample)} records")
        print(f"   • High-risk: {len(high_risk_sample)}")
        print(f"   • Low-risk: {len(low_risk_sample)}")

        return final_sample

    def preview_samples(self, sample_df: pd.DataFrame, n_preview: int = 5):
        """Preview some samples"""
        print(f"\n🔍 PREVIEW OF {n_preview} SAMPLES:")
        print("=" * 80)

        for idx, row in sample_df.head(n_preview).iterrows():
            risk_score = row.get("risk_score", 0)
            content = str(row["content"])[:150] + "..." if len(str(row["content"])) > 150 else str(row["content"])

            print(f"\n[{row['type'].upper()}] Risk Score: {risk_score}")
            print(f"Content: {content}")
            print("-" * 40)


# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Run the complete pipeline"""
    print("🚀 STARTING GENZ CONTENT MODERATION PIPELINE")
    print("=" * 60)

    # Step 1: Load dataset
    df = load_genz_dataset()
    if df is None:
        print("❌ Failed to load dataset. Exiting.")
        return

    # Step 2: Create strategic sample
    sampler = SmartSampler()
    sample_df = sampler.create_sample(df, n_samples=1000)

    # Step 3: Preview samples
    sampler.preview_samples(sample_df, n_preview=5)

    # Step 4: Save for labeling
    columns_for_labeling = ["type", "subreddit", "content", "score", "risk_score"]
    sample_for_labeling = sample_df[columns_for_labeling].copy()
    sample_for_labeling.to_csv("genz_sample_for_labeling.csv", index=False)

    print(f"\n💾 Sample saved to 'genz_sample_for_labeling.csv'")
    print(f"🏷️ Ready for GPT-4o mini labeling!")
    print(f"\n✅ PIPELINE COMPLETE!")


if __name__ == "__main__":
    main()
