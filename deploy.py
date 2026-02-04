#!/usr/bin/env python3
"""
Voxies Complete Deployment System
Single command deployment with tests, logging, and monitoring
"""
import os
import sys
import subprocess
import time
import signal
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from utils.logger import deployment_logger

class VoxiesDeployer:
    """
    Complete deployment system for Voxies services
    """
    
    def __init__(self, debug_mode: bool = True, run_tests: bool = True):
        self.debug_mode = debug_mode
        self.run_tests = run_tests
        self.processes = {}
        self.deployment_start_time = time.time()
        
        deployment_logger.info("Initializing Voxies Deployer", 
                             details=f"Debug: {debug_mode}, Tests: {run_tests}")
    
    def run_command(self, command: List[str], cwd: Optional[str] = None, 
                   capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        deployment_logger.debug(f"Running command: {' '.join(command)}", 
                              details=f"Working directory: {cwd}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            deployment_logger.debug(f"Command completed with exit code: {result.returncode}")
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            deployment_logger.error("Command timed out", error_type="timeout")
            return 1, "", "Command timed out"
        except Exception as e:
            deployment_logger.error(f"Command execution failed: {e}", error_type="command_error")
            return 1, "", str(e)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        deployment_logger.info("Checking prerequisites")
        
        # Check Python version
        if sys.version_info < (3, 8):
            deployment_logger.error("Python 3.8+ required", error_type="version_error")
            return False
        
        # Check required files
        required_files = [
            '.env',
            'agents/requirements.txt',
            'client/requirements.txt',
            'slack_bot/requirements.txt'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                deployment_logger.error(f"Required file missing: {file_path}", 
                                      error_type="missing_file")
                return False
        
        # Check required directories
        required_dirs = ['agents', 'client', 'slack_bot', 'utils', 'tests']
        for dir_path in required_dirs:
            if not os.path.isdir(dir_path):
                deployment_logger.error(f"Required directory missing: {dir_path}", 
                                      error_type="missing_directory")
                return False
        
        deployment_logger.info("✅ All prerequisites met")
        return True
    
    def install_dependencies(self) -> bool:
        """Install all required dependencies"""
        deployment_logger.info("Installing dependencies")
        
        # Install test dependencies
        exit_code, stdout, stderr = self.run_command([
            sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-asyncio'
        ])
        
        if exit_code != 0:
            deployment_logger.error(f"Failed to install test dependencies: {stderr}", 
                                  error_type="dependency_error")
            return False
        
        # Install agents dependencies
        exit_code, stdout, stderr = self.run_command([
            sys.executable, '-m', 'pip', 'install', '-r', 'agents/requirements.txt'
        ])
        
        if exit_code != 0:
            deployment_logger.error(f"Failed to install agents dependencies: {stderr}", 
                                  error_type="dependency_error")
            return False
        
        # Install client dependencies
        exit_code, stdout, stderr = self.run_command([
            sys.executable, '-m', 'pip', 'install', '-r', 'client/requirements.txt'
        ])
        
        if exit_code != 0:
            deployment_logger.error(f"Failed to install client dependencies: {stderr}", 
                                  error_type="dependency_error")
            return False
        
        # Install slack bot dependencies
        exit_code, stdout, stderr = self.run_command([
            sys.executable, '-m', 'pip', 'install', '-r', 'slack_bot/requirements.txt'
        ])
        
        if exit_code != 0:
            deployment_logger.error(f"Failed to install slack bot dependencies: {stderr}", 
                                  error_type="dependency_error")
            return False
        
        deployment_logger.info("✅ All dependencies installed")
        return True
    
    def run_tests_suite(self) -> bool:
        """Run all test cases"""
        if not self.run_tests:
            deployment_logger.info("Skipping tests (disabled)")
            return True
        
        deployment_logger.info("Running test suite")
        
        # Run simplified test runner
        exit_code, stdout, stderr = self.run_command([
            sys.executable, 'run_tests.py'
        ])
        
        if exit_code != 0:
            deployment_logger.error(f"Tests failed: {stderr}", error_type="test_failure")
            return False
        
        deployment_logger.info("✅ All tests passed")
        return True
    
    def setup_configuration(self) -> bool:
        """Setup configuration for deployment"""
        deployment_logger.info("Setting up configuration")
        
        # Update agents config for debug/production mode
        config_content = f'''"""
Agent configuration settings
"""

# Development mode settings
DEV_MODE = {self.debug_mode}  # Debug mode: {self.debug_mode}
SHOW_TOOL_CALLS_IN_DEV = {self.debug_mode}  # Show tool execution details
SHOW_SUPERVISOR_VERIFICATION = {self.debug_mode}  # Show supervisor verification steps

# Agent settings
MAX_ITERATIONS = 20
VERBOSE = {self.debug_mode}

# Constants required by other modules
DEFAULT_MAX_ITERATIONS = 20
DEFAULT_RECURSION_LIMIT = 50
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

# Model configuration
MODEL_OPTIONS = {{
    'OpenAI': 'gpt-4',
    'Antropic': 'claude-3-sonnet-20240229',
    'Bedrock': 'anthropic.claude-3-sonnet-20240229-v1:0',
    'Google': 'gemini-pro'
}}

# Snowflake MCP server configuration
SNOWFLAKE_SERVER_CONFIG = {{
    "command": "python",
    "args": ["snowflake_launcher.py"],
    "env": {{
        "SNOWFLAKE_ACCOUNT": "",  # Will be set from environment
        "SNOWFLAKE_USER": "",     # Will be set from environment  
        "SNOWFLAKE_PASSWORD": "", # Will be set from environment
        "SNOWFLAKE_DATABASE": "", # Will be set from environment
        "SNOWFLAKE_SCHEMA": "",   # Will be set from environment
        "SNOWFLAKE_WAREHOUSE": "" # Will be set from environment
    }}
}}
'''
        
        with open('agents/config.py', 'w') as f:
            f.write(config_content)
        
        deployment_logger.info(f"✅ Configuration set for {'debug' if self.debug_mode else 'production'} mode")
        return True
    
    def stop_existing_services(self) -> bool:
        """Stop any existing services"""
        deployment_logger.info("Stopping existing services")
        
        # Kill existing processes
        commands = [
            ['pkill', '-f', 'streamlit run'],
            ['pkill', '-f', 'python.*bot.py']
        ]
        
        for cmd in commands:
            self.run_command(cmd, capture_output=True)
        
        time.sleep(2)  # Wait for processes to stop
        deployment_logger.info("✅ Existing services stopped")
        return True
    
    def start_streamlit(self) -> bool:
        """Start Streamlit service"""
        deployment_logger.info("Starting Streamlit service")
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        try:
            # Start Streamlit in background with proper PYTHONPATH
            cmd = [
                sys.executable, '-m', 'streamlit', 'run', 'app.py',
                '--server.port=8501',
                '--server.address=0.0.0.0',
                f'--logger.level={"debug" if self.debug_mode else "info"}'
            ]
            
            # Set environment with PYTHONPATH
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.abspath('.')
            
            with open('logs/streamlit.log', 'w') as log_file:
                process = subprocess.Popen(
                    cmd,
                    cwd='client',
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env
                )
            
            self.processes['streamlit'] = process
            
            # Wait for startup
            time.sleep(5)
            
            # Check if process is still running
            if process.poll() is None:
                deployment_logger.info("✅ Streamlit service started successfully")
                deployment_logger.log_performance("streamlit_startup", 5000, success=True)
                return True
            else:
                deployment_logger.error("Streamlit service failed to start", error_type="startup_error")
                return False
                
        except Exception as e:
            deployment_logger.error(f"Failed to start Streamlit: {e}", error_type="startup_error")
            return False
    
    def start_slack_bot(self) -> bool:
        """Start Slack bot service"""
        deployment_logger.info("Starting Slack bot service")
        
        try:
            # Start Slack bot in background with proper PYTHONPATH
            cmd = [sys.executable, 'run_bot.py']
            
            # Set environment with PYTHONPATH
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.abspath('.')
            
            with open('logs/slack_bot.log', 'w') as log_file:
                process = subprocess.Popen(
                    cmd,
                    cwd='slack_bot',
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env
                )
            
            self.processes['slack_bot'] = process
            
            # Wait for startup
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                deployment_logger.info("✅ Slack bot service started successfully")
                deployment_logger.log_performance("slack_bot_startup", 3000, success=True)
                return True
            else:
                deployment_logger.error("Slack bot service failed to start", error_type="startup_error")
                return False
                
        except Exception as e:
            deployment_logger.error(f"Failed to start Slack bot: {e}", error_type="startup_error")
            return False
    
    def monitor_services(self) -> Dict[str, bool]:
        """Monitor service health"""
        deployment_logger.info("Monitoring service health")
        
        status = {}
        
        for service_name, process in self.processes.items():
            if process.poll() is None:
                status[service_name] = True
                deployment_logger.info(f"✅ {service_name} is running (PID: {process.pid})")
            else:
                status[service_name] = False
                deployment_logger.error(f"❌ {service_name} has stopped", error_type="service_failure")
        
        return status
    
    def save_deployment_info(self) -> None:
        """Save deployment information"""
        deployment_info = {
            'timestamp': time.time(),
            'debug_mode': self.debug_mode,
            'processes': {name: proc.pid for name, proc in self.processes.items() if proc.poll() is None},
            'duration_seconds': time.time() - self.deployment_start_time
        }
        
        with open('logs/deployment_info.txt', 'w') as f:
            f.write(f"Deployment Info\n")
            f.write(f"===============\n")
            f.write(f"Timestamp: {time.ctime(deployment_info['timestamp'])}\n")
            f.write(f"Debug Mode: {deployment_info['debug_mode']}\n")
            f.write(f"Duration: {deployment_info['duration_seconds']:.2f} seconds\n")
            f.write(f"\nRunning Services:\n")
            for service, pid in deployment_info['processes'].items():
                f.write(f"  {service}: PID {pid}\n")
            f.write(f"\nAccess URLs:\n")
            f.write(f"  Streamlit: http://localhost:8501\n")
            f.write(f"  Slack Bot: Active (responds to @mentions and /voxies)\n")
            f.write(f"\nLogs:\n")
            f.write(f"  Streamlit: tail -f logs/streamlit.log\n")
            f.write(f"  Slack Bot: tail -f logs/slack_bot.log\n")
            f.write(f"  CSV Logs: logs/*_operations.csv, logs/*_errors.csv, logs/*_performance.csv\n")
            f.write(f"\nStop Services:\n")
            f.write(f"  python deploy.py --stop\n")
    
    def stop_services(self) -> None:
        """Stop all running services"""
        deployment_logger.info("Stopping all services")
        
        for service_name, process in self.processes.items():
            if process.poll() is None:
                deployment_logger.info(f"Stopping {service_name} (PID: {process.pid})")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    deployment_logger.warning(f"Force killing {service_name}")
                    process.kill()
                    process.wait()
                
                deployment_logger.info(f"✅ {service_name} stopped")
        
        self.processes.clear()
        deployment_logger.info("✅ All services stopped")
    
    def deploy(self) -> bool:
        """Main deployment function"""
        deployment_logger.info("Starting Voxies deployment")
        
        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: Install dependencies
            if not self.install_dependencies():
                return False
            
            # Step 3: Run tests
            if not self.run_tests_suite():
                return False
            
            # Step 4: Setup configuration
            if not self.setup_configuration():
                return False
            
            # Step 5: Stop existing services
            if not self.stop_existing_services():
                return False
            
            # Step 6: Start services
            if not self.start_streamlit():
                return False
            
            # Try to start Slack bot (optional)
            slack_success = self.start_slack_bot()
            if not slack_success:
                deployment_logger.warning("Slack bot failed to start, continuing with Streamlit only")
                print("⚠️  Slack bot failed to start, but Streamlit is running")
            
            # Step 7: Monitor services
            status = self.monitor_services()
            
            # Step 8: Save deployment info
            self.save_deployment_info()
            
            # Final status
            total_duration = time.time() - self.deployment_start_time
            deployment_logger.log_performance("full_deployment", total_duration * 1000, success=True)
            
            # Check if at least Streamlit is running
            streamlit_running = status.get('streamlit', False)
            if streamlit_running:
                deployment_logger.info(f"🎉 Deployment completed successfully in {total_duration:.2f} seconds")
                return True
            else:
                deployment_logger.error("Critical failure: Streamlit service not running")
                return False
            
        except Exception as e:
            deployment_logger.error(f"Deployment failed: {e}", error_type="deployment_error")
            return False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            deployment_logger.info(f"Received signal {signum}, shutting down...")
            self.stop_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

def main():
    parser = argparse.ArgumentParser(description='Voxies Complete Deployment System')
    parser.add_argument('--debug', action='store_true', default=True,
                       help='Enable debug mode (default: True)')
    parser.add_argument('--no-debug', action='store_true',
                       help='Disable debug mode')
    parser.add_argument('--no-tests', action='store_true',
                       help='Skip running tests')
    parser.add_argument('--stop', action='store_true',
                       help='Stop running services')
    
    args = parser.parse_args()
    
    # Handle debug mode
    debug_mode = args.debug and not args.no_debug
    run_tests = not args.no_tests
    
    deployer = VoxiesDeployer(debug_mode=debug_mode, run_tests=run_tests)
    
    if args.stop:
        # Read existing process info and stop services
        deployer.stop_services()
        return
    
    # Setup signal handlers
    deployer.setup_signal_handlers()
    
    # Run deployment
    success = deployer.deploy()
    
    if success:
        print("\n🎉 Voxies Deployment Successful!")
        print("=" * 50)
        print("📊 Services Status:")
        status = deployer.monitor_services()
        for service, running in status.items():
            print(f"  {'✅' if running else '❌'} {service}: {'Running' if running else 'Stopped'}")
        
        print("\n🌐 Access Points:")
        print("  • Streamlit App: http://localhost:8501")
        print("  • Slack Bot: Active (responds to @mentions and /voxies)")
        
        print("\n📝 Logs:")
        print("  • Operations: logs/*_operations.csv")
        print("  • Errors: logs/*_errors.csv") 
        print("  • Performance: logs/*_performance.csv")
        print("  • Service Logs: logs/streamlit.log, logs/slack_bot.log")
        
        print("\n🛑 To stop services:")
        print("  python deploy.py --stop")
        
        print(f"\n🔍 Debug Mode: {'Enabled' if debug_mode else 'Disabled'}")
        
        # Keep script running to monitor services
        try:
            while True:
                time.sleep(30)
                status = deployer.monitor_services()
                if not all(status.values()):
                    deployment_logger.error("Service failure detected", error_type="service_monitoring")
                    break
        except KeyboardInterrupt:
            deployer.stop_services()
    else:
        print("\n❌ Deployment Failed!")
        print("Check logs for details: logs/deployment_*.csv")
        sys.exit(1)

if __name__ == "__main__":
    main() 