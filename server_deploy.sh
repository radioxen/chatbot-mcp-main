#!/bin/bash

# =============================================================================
# Voxies Server Deployment Script
# Single command to deploy both Streamlit app and Slack bot on Linux server
# Usage: ./server_deploy.sh [production]
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Configuration
REPO_URL="https://github.com/AlwaysGeeky-Games/voxies-chatbot.git"
PROJECT_DIR="/opt/voxies"
SERVICE_USER="voxies"
PRODUCTION_MODE=${1:-"development"}

echo -e "${BLUE}🚀 Voxies Server Deployment${NC}"
echo "============================="
echo "Mode: $PRODUCTION_MODE"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_info "Running as root - will create service user"
else
   log_warning "Not running as root - using current user"
   SERVICE_USER=$(whoami)
fi

# Install system dependencies
log_info "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv git nginx supervisor
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum update -y
    sudo yum install -y python3 python3-pip git nginx supervisor
elif command -v dnf &> /dev/null; then
    # Fedora
    sudo dnf update -y
    sudo dnf install -y python3 python3-pip git nginx supervisor
else
    log_error "Unsupported package manager. Please install Python 3, pip, git, nginx, and supervisor manually."
    exit 1
fi

# Create service user if running as root
if [[ $EUID -eq 0 ]] && ! id "$SERVICE_USER" &>/dev/null; then
    log_info "Creating service user: $SERVICE_USER"
    sudo useradd -r -s /bin/bash -d $PROJECT_DIR $SERVICE_USER
fi

# Create project directory
log_info "Setting up project directory: $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

# Switch to project directory
cd $PROJECT_DIR

# Clone or update repository
if [ -d ".git" ]; then
    log_info "Updating existing repository..."
    sudo -u $SERVICE_USER git pull origin main
else
    log_info "Cloning repository..."
    sudo -u $SERVICE_USER git clone $REPO_URL .
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_error ".env file not found! Please copy your .env file to $PROJECT_DIR"
    log_info "You can use: scp .env user@server:$PROJECT_DIR/"
    exit 1
fi

# Set up Python virtual environment
log_info "Setting up Python virtual environment..."
sudo -u $SERVICE_USER python3 -m venv venv
sudo -u $SERVICE_USER ./venv/bin/pip install --upgrade pip

# Install Python dependencies
log_info "Installing Python dependencies..."

# Install agents dependencies
if [ -f "agents/requirements.txt" ]; then
    sudo -u $SERVICE_USER ./venv/bin/pip install -r agents/requirements.txt
fi

# Install Streamlit dependencies
if [ -f "client/requirements.txt" ]; then
    sudo -u $SERVICE_USER ./venv/bin/pip install -r client/requirements.txt
fi

# Install Slack bot dependencies
if [ -f "slack_bot/requirements.txt" ]; then
    sudo -u $SERVICE_USER ./venv/bin/pip install -r slack_bot/requirements.txt
else
    # Install common Slack bot dependencies
    sudo -u $SERVICE_USER ./venv/bin/pip install slack-bolt python-dotenv
fi

# Set production or development mode
log_info "Configuring application mode: $PRODUCTION_MODE"
if [ "$PRODUCTION_MODE" = "production" ]; then
    # Production configuration
    sudo -u $SERVICE_USER cat > agents/config.py << 'EOF'
"""
Agent configuration settings - PRODUCTION MODE
"""

# Development mode settings
DEV_MODE = False  # Production deployment
SHOW_TOOL_CALLS_IN_DEV = False  # Hide tool execution details in production
SHOW_SUPERVISOR_VERIFICATION = False  # Hide supervisor verification steps

# Agent settings
MAX_ITERATIONS = 20
VERBOSE = False

# Snowflake MCP server configuration
SNOWFLAKE_SERVER_CONFIG = {
    "command": "python",
    "args": ["snowflake_launcher.py"],
    "env": {
        "SNOWFLAKE_ACCOUNT": "",  # Will be set from environment
        "SNOWFLAKE_USER": "",     # Will be set from environment  
        "SNOWFLAKE_PASSWORD": "", # Will be set from environment
        "SNOWFLAKE_DATABASE": "", # Will be set from environment
        "SNOWFLAKE_SCHEMA": "",   # Will be set from environment
        "SNOWFLAKE_WAREHOUSE": "" # Will be set from environment
    }
}
EOF
else
    # Development configuration
    sudo -u $SERVICE_USER cat > agents/config.py << 'EOF'
"""
Agent configuration settings - DEVELOPMENT MODE
"""

# Development mode settings
DEV_MODE = True  # Development deployment
SHOW_TOOL_CALLS_IN_DEV = True  # Show tool execution details
SHOW_SUPERVISOR_VERIFICATION = True  # Show supervisor verification steps

# Agent settings
MAX_ITERATIONS = 20
VERBOSE = True

# Snowflake MCP server configuration
SNOWFLAKE_SERVER_CONFIG = {
    "command": "python",
    "args": ["snowflake_launcher.py"],
    "env": {
        "SNOWFLAKE_ACCOUNT": "",  # Will be set from environment
        "SNOWFLAKE_USER": "",     # Will be set from environment  
        "SNOWFLAKE_PASSWORD": "", # Will be set from environment
        "SNOWFLAKE_DATABASE": "", # Will be set from environment
        "SNOWFLAKE_SCHEMA": "",   # Will be set from environment
        "SNOWFLAKE_WAREHOUSE": "" # Will be set from environment
    }
}
EOF
fi

# Create logs directory
sudo -u $SERVICE_USER mkdir -p logs

# Get server IP for configuration
SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')

# Configure Nginx for Streamlit
log_info "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/voxies << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/voxies /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Configure Supervisor for process management
log_info "Configuring Supervisor..."
sudo tee /etc/supervisor/conf.d/voxies-streamlit.conf << EOF
[program:voxies-streamlit]
command=$PROJECT_DIR/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1
directory=$PROJECT_DIR/client
user=$SERVICE_USER
autostart=true
autorestart=true
stderr_logfile=$PROJECT_DIR/logs/streamlit.err.log
stdout_logfile=$PROJECT_DIR/logs/streamlit.out.log
environment=PATH="$PROJECT_DIR/venv/bin"
EOF

sudo tee /etc/supervisor/conf.d/voxies-slack-bot.conf << EOF
[program:voxies-slack-bot]
command=$PROJECT_DIR/venv/bin/python bot.py
directory=$PROJECT_DIR/slack_bot
user=$SERVICE_USER
autostart=true
autorestart=true
stderr_logfile=$PROJECT_DIR/logs/slack_bot.err.log
stdout_logfile=$PROJECT_DIR/logs/slack_bot.out.log
environment=PATH="$PROJECT_DIR/venv/bin"
EOF

# Reload and start services
log_info "Starting services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start voxies-streamlit
sudo supervisorctl start voxies-slack-bot

# Wait for services to start
sleep 10

# Check service status
log_info "Checking service status..."
STREAMLIT_STATUS=$(sudo supervisorctl status voxies-streamlit | awk '{print $2}')
SLACK_BOT_STATUS=$(sudo supervisorctl status voxies-slack-bot | awk '{print $2}')

echo
log_success "🎉 Deployment completed!"
echo
echo "📊 Service Status:"
echo "  • Streamlit App: $STREAMLIT_STATUS"
echo "  • Slack Bot: $SLACK_BOT_STATUS"
echo
echo "🌐 Access your application:"
echo "  • Web Interface: http://$SERVER_IP"
echo "  • Local Streamlit: http://localhost:8501"
echo
echo "📝 Logs:"
echo "  • Streamlit: sudo tail -f $PROJECT_DIR/logs/streamlit.out.log"
echo "  • Slack Bot: sudo tail -f $PROJECT_DIR/logs/slack_bot.out.log"
echo "  • Error logs: sudo tail -f $PROJECT_DIR/logs/*.err.log"
echo
echo "🔧 Service Management:"
echo "  • Restart Streamlit: sudo supervisorctl restart voxies-streamlit"
echo "  • Restart Slack Bot: sudo supervisorctl restart voxies-slack-bot"
echo "  • View status: sudo supervisorctl status"
echo
echo "🔄 To redeploy:"
echo "  • cd $PROJECT_DIR && ./server_deploy.sh"

log_success "Deployment ready! 🚀" 