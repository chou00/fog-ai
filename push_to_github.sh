#!/bin/bash

# Bash script to push to GitHub
# Usage: ./push_to_github.sh

echo "========================================"
echo "Push to GitHub - Fog AI Anomaly Detection"
echo "========================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed!"
    exit 1
fi

echo "Git found: $(git --version)"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "Error: Not a git repository. Run 'git init' first."
    exit 1
fi

# Check if remote exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -n "$REMOTE_URL" ]; then
    echo "Remote 'origin' already exists: $REMOTE_URL"
    read -p "Use existing remote? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
        REMOTE_URL=""
    fi
fi

# If no remote, ask for GitHub URL
if [ -z "$REMOTE_URL" ]; then
    echo ""
    echo "Please provide your GitHub repository URL:"
    echo "Example: https://github.com/USERNAME/fog-ai-anomaly-detection.git"
    read -p "GitHub URL: " GITHUB_URL
    
    if [ -n "$GITHUB_URL" ]; then
        git remote add origin "$GITHUB_URL"
        echo "Remote 'origin' added: $GITHUB_URL"
        REMOTE_URL="$GITHUB_URL"
    else
        echo "No URL provided. Exiting."
        exit 1
    fi
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo ""
echo "Current branch: $CURRENT_BRANCH"

# Ask to rename to main if needed
if [ "$CURRENT_BRANCH" != "main" ]; then
    read -p "Rename branch to 'main'? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -M main
        echo "Branch renamed to 'main'"
    fi
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
echo ""

if git push -u origin main; then
    echo ""
    echo "========================================"
    echo "Success! Code pushed to GitHub"
    echo "========================================"
    echo ""
    echo "On Kali Linux, clone with:"
    echo "  git clone $REMOTE_URL"
else
    echo ""
    echo "Error pushing to GitHub!"
    echo "Make sure:"
    echo "  1. The repository exists on GitHub"
    echo "  2. You have push permissions"
    echo "  3. You're authenticated"
    echo ""
    echo "See GIT_SETUP.md for detailed instructions"
    exit 1
fi

