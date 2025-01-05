# src/schedulers/priority.py
from typing import Optional, List
from .base_scheduler import BaseScheduler
from ..process.process import Process
from ..process.process_state import ProcessState

class PriorityScheduler(BaseScheduler):
    """
    Priority-based CPU Scheduler Implementation
    Processes are executed based on priority level (higher priority gets CPU first)
    """
    
    def __init__(self, preemptive: bool = True):
        """
        Initialize Priority Scheduler
        
        Args:
            preemptive: If True, higher priority process can preempt running process
        """
        super().__init__()
        self.preemptive = preemptive
    
    def add_process(self, process: Process) -> None:
        """Add new process to scheduler"""
        self.processes.append(process)
    
    def get_next_process(self) -> Optional[Process]:
        """
        Get highest priority ready process
        
        Returns:
            Process with highest priority (lowest priority number)
        """
        ready_processes = [p for p in self.processes if p.state == ProcessState.READY]
        if not ready_processes:
            return None
        return min(ready_processes, key=lambda p: (p.priority, p.arrival_time))
    
    def should_preempt(self, running_process: Process, ready_process: Process) -> bool:
        """Check if ready process should preempt running process"""
        return (self.preemptive and 
                ready_process.priority < running_process.priority)
    
    def run(self) -> None:
        """Run priority scheduling simulation"""
        while not self.is_all_completed():
            self.update_process_states()
            
            # Check for preemption
            if self.current_process and self.preemptive:
                next_process = self.get_next_process()
                if (next_process and 
                    self.should_preempt(self.current_process, next_process)):
                    self.current_process.update_state(ProcessState.READY)
                    self.current_process = None
            
            # Get next process if none running
            if self.current_process is None:
                self.current_process = self.get_next_process()
                if self.current_process:
                    self.current_process.update_state(ProcessState.RUNNING)
                    if self.current_process.start_time is None:
                        self.current_process.start_time = self.current_time
            
            # Execute current process
            if self.current_process:
                time_used = self.current_process.execute(1)
                
                if self.current_process.is_completed():
                    self.current_process.completion_time = self.current_time + 1
                    self.current_process.turnaround_time = (
                        self.current_process.completion_time - 
                        self.current_process.arrival_time
                    )
                    self.current_process = None
            
            self.update_waiting_times()
            self.current_time += 1