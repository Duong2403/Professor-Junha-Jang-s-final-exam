# src/interrupt/timer.py
from dataclasses import dataclass
from typing import Callable, Optional
import time

@dataclass
class TimerInterrupt:
    """
    Implements a timer interrupt mechanism for CPU scheduling
    
    Timer interrupts are used to implement preemptive scheduling by
    interrupting the currently running process after a specified time quantum
    """
    quantum: int  # Time quantum for each process execution
    handler: Callable  # Function to call when timer expires
    
    def __post_init__(self):
        """Initialize timer state"""
        self.start_time: Optional[float] = None
        self.is_running: bool = False
    
    def start(self) -> None:
        """Start the timer"""
        self.start_time = time.time()
        self.is_running = True
    
    def stop(self) -> None:
        """Stop the timer"""
        self.start_time = None
        self.is_running = False
    
    def check(self) -> bool:
        """
        Check if timer has expired
        
        Returns:
            bool: True if quantum has elapsed, False otherwise
        """
        if not self.is_running or self.start_time is None:
            return False
            
        elapsed = time.time() - self.start_time
        if elapsed >= self.quantum:
            self.handler()  # Call interrupt handler
            return True
        return False

    def reset(self) -> None:
        """Reset the timer for a new quantum"""
        self.stop()
        self.start()