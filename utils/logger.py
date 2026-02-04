"""
Comprehensive Logging System for Voxies Services
Logs all operations, errors, warnings to CSV files with timestamps
"""
import csv
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class VoxiesLogger:
    """
    Centralized logging system that writes to CSV files
    """
    
    def __init__(self, service_name: str = "voxies", log_dir: str = "logs"):
        self.service_name = service_name
        self.log_dir = log_dir
        self.ensure_log_dir()
        
        # CSV file paths
        self.operations_log = os.path.join(log_dir, f"{service_name}_operations.csv")
        self.errors_log = os.path.join(log_dir, f"{service_name}_errors.csv")
        self.performance_log = os.path.join(log_dir, f"{service_name}_performance.csv")
        
        # Initialize CSV files with headers
        self._init_csv_files()
    
    def ensure_log_dir(self):
        """Ensure log directory exists"""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _init_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        # Operations log
        if not os.path.exists(self.operations_log):
            with open(self.operations_log, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'service', 'level', 'operation', 'status', 
                    'message', 'details', 'user_id', 'session_id'
                ])
        
        # Errors log
        if not os.path.exists(self.errors_log):
            with open(self.errors_log, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'service', 'level', 'error_type', 'message', 
                    'stack_trace', 'context', 'user_id'
                ])
        
        # Performance log
        if not os.path.exists(self.performance_log):
            with open(self.performance_log, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'service', 'operation', 'duration_ms', 
                    'input_size', 'output_size', 'tool_count', 'success'
                ])
    
    def log_operation(
        self, 
        level: LogLevel, 
        operation: str, 
        status: str, 
        message: str,
        details: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Log general operations"""
        try:
            with open(self.operations_log, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    self.service_name,
                    level.value,
                    operation,
                    status,
                    message,
                    details or "",
                    user_id or "",
                    session_id or ""
                ])
        except Exception as e:
            print(f"Logging error: {e}", file=sys.stderr)
    
    def log_error(
        self,
        level: LogLevel,
        error_type: str,
        message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict] = None,
        user_id: Optional[str] = None
    ):
        """Log errors and exceptions"""
        try:
            with open(self.errors_log, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    self.service_name,
                    level.value,
                    error_type,
                    message,
                    stack_trace or "",
                    str(context) if context else "",
                    user_id or ""
                ])
        except Exception as e:
            print(f"Error logging error: {e}", file=sys.stderr)
    
    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        input_size: int = 0,
        output_size: int = 0,
        tool_count: int = 0,
        success: bool = True
    ):
        """Log performance metrics"""
        try:
            with open(self.performance_log, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    self.service_name,
                    operation,
                    round(duration_ms, 2),
                    input_size,
                    output_size,
                    tool_count,
                    success
                ])
        except Exception as e:
            print(f"Performance logging error: {e}", file=sys.stderr)
    
    def log_query(
        self,
        query: str,
        response: str,
        tool_count: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        success: bool = True
    ):
        """Log query operations with input/output"""
        self.log_operation(
            LogLevel.INFO,
            "query_processing",
            "success" if success else "failed",
            f"Query processed: {query[:100]}..." if len(query) > 100 else query,
            f"Response length: {len(response)}, Tools used: {tool_count}",
            user_id
        )
        
        self.log_performance(
            "query_processing",
            duration_ms,
            len(query),
            len(response),
            tool_count,
            success
        )
    
    def debug(self, message: str, **kwargs):
        """Debug level logging"""
        self.log_operation(LogLevel.DEBUG, "debug", "info", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Info level logging"""
        self.log_operation(LogLevel.INFO, "info", "success", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning level logging"""
        self.log_operation(LogLevel.WARNING, "warning", "warning", message, **kwargs)
    
    def error(self, message: str, error_type: str = "general", **kwargs):
        """Error level logging"""
        self.log_error(LogLevel.ERROR, error_type, message, **kwargs)
    
    def critical(self, message: str, error_type: str = "critical", **kwargs):
        """Critical level logging"""
        self.log_error(LogLevel.CRITICAL, error_type, message, **kwargs)

# Global logger instances
streamlit_logger = VoxiesLogger("streamlit")
slack_logger = VoxiesLogger("slack_bot")
deployment_logger = VoxiesLogger("deployment") 