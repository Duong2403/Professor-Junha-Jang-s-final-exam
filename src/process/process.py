# src/process/process.py
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from .process_state import ProcessState

@dataclass
class Process:
    """Represents a process in the system"""
    # Core attributes
    pid: int
    arrival_time: int
    burst_time: int
    priority: int = 0
    
    # State management
    state: ProcessState = field(default=ProcessState.NEW)
    remaining_time: int = field(init=False)
    
    # Performance metrics
    waiting_time: int = field(default=0)
    turnaround_time: int = field(default=0)
    response_time: Optional[int] = field(default=None)
    context_switches: int = field(default=0)  # Thêm dòng này
    
    # Timestamps
    start_time: Optional[int] = field(default=None)
    completion_time: Optional[int] = field(default=None)
    last_state_change: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize after creation"""
        self.remaining_time = self.burst_time
    
    def update_state(self, new_state: ProcessState) -> None:
        """Update process state"""
        if self.state != new_state:
            self.state = new_state
            self.last_state_change = datetime.now()
            if new_state == ProcessState.RUNNING:
                self.context_switches += 1  # Tăng số context switches
    
    def execute(self, time_quantum: int) -> int:
        """Execute process for given time quantum"""
        if self.state != ProcessState.RUNNING:
            raise ValueError("Cannot execute: process not in RUNNING state")
            
        time_used = min(time_quantum, self.remaining_time)
        self.remaining_time -= time_used
        
        if self.remaining_time == 0:
            self.update_state(ProcessState.TERMINATED)
            
        return time_used
    
    def is_completed(self) -> bool:
        """Check if process has completed"""
        return self.state == ProcessState.TERMINATED