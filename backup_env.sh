#!/bin/bash
# Backup .env file with timestamp
if [ -f ".env" ]; then
    timestamp=$(date +"%Y%m%d_%H%M%S")
    cp .env ".env.backup_$timestamp"
    echo "✅ Backed up .env to .env.backup_$timestamp"
else
    echo "❌ No .env file found to backup"
fi 