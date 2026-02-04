#!/bin/bash

# =============================================================================
# Commit and Push to GitHub
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo -e "${BLUE}📦 Committing and Pushing to GitHub${NC}"
echo "===================================="

# Check if .env file exists and warn about it
if [ -f ".env" ]; then
    log_warning ".env file detected - ensuring it's in .gitignore"
    if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
        echo ".env" >> .gitignore
        log_info "Added .env to .gitignore"
    fi
fi

# Add all files except .env
log_info "Adding files to git..."
git add .
git reset HEAD .env 2>/dev/null || true  # Remove .env if accidentally added

# Show status
log_info "Git status:"
git status --short

# Commit with timestamp
COMMIT_MSG="Deploy: Complete Voxies service deployment - $(date '+%Y-%m-%d %H:%M:%S')"
log_info "Committing with message: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || {
    log_warning "No changes to commit"
    exit 0
}

# Push to main branch
log_info "Pushing to GitHub..."
git push origin main

log_success "Successfully pushed to GitHub! 🚀"
echo
echo "📋 Next steps:"
echo "1. Copy your .env file to the server"
echo "2. Update the REPO_URL in server_deploy.sh with your GitHub repository"
echo "3. Run ./server_deploy.sh on your Linux server" 