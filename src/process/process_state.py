# src/process/process_state.py
from enum import Enum

class ProcessState(Enum):
    """Defines possible states of a process in the system"""
    NEW = "NEW"           # Process has just been created
    READY = "READY"       # Process is ready to be executed
    RUNNING = "RUNNING"   # Process is currently executing
    WAITING = "WAITING"   # Process is waiting for I/O or an event
    TERMINATED = "TERMINATED"  # Process has finished execution