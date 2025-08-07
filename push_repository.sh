#!/bin/bash

echo "🚀 Pushing HarmonyMigrator to GitHub..."
echo "Repository: https://github.com/saurabh-yergattikar/harmony-migrator"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in the harmony-migrator directory"
    exit 1
fi

# Check git status
echo "📊 Git Status:"
git status --porcelain

# Add any new files
echo "📁 Adding files..."
git add .

# Commit if there are changes
if [ -n "$(git status --porcelain)" ]; then
    echo "💾 Committing changes..."
    git commit -m "Update: HarmonyMigrator - OpenAI to GPT-OSS migration tool"
fi

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 Repository URL: https://github.com/saurabh-yergattikar/harmony-migrator"
    echo ""
    echo "📋 Next steps:"
    echo "1. Add a description to your repository"
    echo "2. Add topics: openai, harmony, gpt-oss, migration, ai, python"
    echo "3. Enable Issues and Discussions"
    echo "4. Add a GitHub Action for CI/CD"
else
    echo "❌ Failed to push. Make sure the repository exists on GitHub."
    echo "💡 Create the repository at: https://github.com/saurabh-yergattikar/harmony-migrator"
fi 