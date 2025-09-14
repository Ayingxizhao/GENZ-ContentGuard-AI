#!/usr/bin/env python3
"""
Script to run malicious post extraction with Hugging Face authentication
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_huggingface_auth():
    """Setup Hugging Face authentication"""
    print("🔐 Setting up Hugging Face authentication...")
    
    # Check if huggingface_hub is installed
    try:
        import huggingface_hub
    except ImportError:
        print("Installing huggingface_hub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
    
    # Check if user is logged in
    try:
        from huggingface_hub import whoami
        user_info = whoami()
        print(f"✅ Already logged in as: {user_info['name']}")
        return True
    except Exception:
        print("❌ Not logged in to Hugging Face")
        print("Please run: huggingface-cli login")
        print("Or set HF_TOKEN environment variable")
        return False

def run_extraction():
    """Run the malicious post extraction"""
    print("\n🚀 Starting malicious post extraction...")
    
    # Run the extraction script
    cmd = [
        sys.executable, "malicious_post_extractor.py",
        "--min-posts", "1000",
        "--max-posts", "5000",
        "--confidence", "0.7",
        "--output", "malicious_posts_extracted.csv"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Extraction completed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Extraction failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    """Main function"""
    print("🛡️ GenZ Content Moderation - Malicious Post Extractor")
    print("=" * 60)
    
    # Check if model exists
    if not Path("genz_detector_model.pkl").exists():
        print("❌ Model file 'genz_detector_model.pkl' not found!")
        print("Please ensure the model is trained and available.")
        return False
    
    # Setup authentication
    if not setup_huggingface_auth():
        print("\n⚠️  Authentication required. Please:")
        print("1. Run: huggingface-cli login")
        print("2. Or set HF_TOKEN environment variable")
        print("3. Then run this script again")
        return False
    
    # Run extraction
    success = run_extraction()
    
    if success:
        print("\n📊 Extraction Results:")
        print("- malicious_posts_extracted.csv: Main output")
        print("- malicious_posts_extracted_summary.txt: Summary report")
        print("- malicious_extraction.log: Detailed log")
        
        # Show file sizes
        csv_file = Path("malicious_posts_extracted.csv")
        if csv_file.exists():
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"- CSV file size: {size_mb:.2f} MB")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
