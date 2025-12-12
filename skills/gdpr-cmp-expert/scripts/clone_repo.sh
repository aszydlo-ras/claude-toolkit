#!/bin/bash
# Clone a GDPR CMP repository using GitHub CLI
# Usage: ./clone_repo.sh <repo_name> [target_directory]

REPO_NAME=$1
TARGET_DIR=${2:-.}
ORG="Ringier-Axel-Springer-PL"

# Available repositories
AVAILABLE_REPOS=(
    "gdpr-popup"
    "adp-datalayer-api"
    "gdpr"
    "gdpr-admin-panel"
    "gdpr-mobile-api"
    "gdpr-mobile-frame"
    "gdpr-db"
    "gdpr-ls-processor"
    "gdpr-dsa-pages"
    "gdpr-dsa-db"
    "gdpr-uptime"
    "gdpr-iab-files"
)

# Print usage if no arguments
if [ -z "$REPO_NAME" ]; then
    echo "Usage: clone_repo.sh <repo_name> [target_directory]"
    echo ""
    echo "Available repositories:"
    for repo in "${AVAILABLE_REPOS[@]}"; do
        echo "  - $repo"
    done
    exit 1
fi

# Validate repository name
VALID_REPO=false
for repo in "${AVAILABLE_REPOS[@]}"; do
    if [ "$repo" == "$REPO_NAME" ]; then
        VALID_REPO=true
        break
    fi
done

if [ "$VALID_REPO" == "false" ]; then
    echo "Error: '$REPO_NAME' is not a valid GDPR repository."
    echo ""
    echo "Available repositories:"
    for repo in "${AVAILABLE_REPOS[@]}"; do
        echo "  - $repo"
    done
    exit 1
fi

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install it with: brew install gh"
    echo "Then authenticate with: gh auth login"
    exit 1
fi

# Check if already exists
if [ -d "$TARGET_DIR/$REPO_NAME" ]; then
    echo "Repository $REPO_NAME already exists in $TARGET_DIR"
    exit 0
fi

# Clone the repository
echo "Cloning $ORG/$REPO_NAME to $TARGET_DIR..."
cd "$TARGET_DIR" && gh repo clone "$ORG/$REPO_NAME"

if [ $? -eq 0 ]; then
    echo "Successfully cloned $REPO_NAME"
else
    echo "Failed to clone $REPO_NAME"
    echo "Make sure you have access to $ORG organization on GitHub"
    exit 1
fi
