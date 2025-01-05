# src/utils/logger.py
import logging
from typing import Optional
import sys
from datetime import datetime

class SchedulerLogger:
    """
    Complete logging system for CPU Scheduler
    """
    def __init__(self, 
                 name: str = "CPUScheduler",
                 level: int = logging.INFO,
                 log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create formatters
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
    def log_process_state_change(self, 
                               process_id: int, 
                               old_state: str, 
                               new_state: str,
                               current_time: int) -> None:
        """Log process state changes"""
        self.logger.info(
            f"Time {current_time}: Process {process_id} "
            f"state changed: {old_state} -> {new_state}"
        )
    
    def log_scheduling_event(self, 
                           event_type: str, 
                           details: str,
                           current_time: int) -> None:
        """Log scheduling events"""
        self.logger.info(
            f"Time {current_time}: {event_type} - {details}"
        )
        
    def log_context_switch(self, 
                          from_pid: Optional[int], 
                          to_pid: Optional[int],
                          current_time: int) -> None:
        """Log context switches"""
        from_str = f"P{from_pid}" if from_pid is not None else "None"
        to_str = f"P{to_pid}" if to_pid is not None else "None"
        self.logger.info(
            f"Time {current_time}: Context Switch: {from_str} -> {to_str}"
        )
        
    def log_metrics(self, metrics: dict) -> None:
        """Log performance metrics"""
        self.logger.info("Performance Metrics:")
        for metric, value in metrics.items():
            self.logger.info(f"  {metric}: {value}")