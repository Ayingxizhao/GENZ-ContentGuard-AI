#!/bin/bash

# Navigate to your project
cd ~/desktop/research/genzLang || { echo "❌ Directory not found"; exit 1; }

# Add all changes
git add .

# Commit with provided message, default to "Update"
msg=${1:-"Update"}
git commit -m "$msg" --no-verify

# Ensure correct remote URL (update if needed)
git remote set-url origin https://github.com/Ayingxizhao/GENZ-ContentGuard-AI.git

# Push to main
git push origin main
