# src/schedulers/sjf.py
from typing import Optional
from .base_scheduler import BaseScheduler
from ..process.process import Process
from ..process.process_state import ProcessState

class SJFScheduler(BaseScheduler):
    """
    Shortest Job First (SJF) Scheduler Implementation
    
    Non-preemptive scheduler that selects the process with shortest burst time
    """
    
    def add_process(self, process: Process) -> None:
        """Add a new process to the scheduler"""
        self.processes.append(process)
    
    def get_next_process(self) -> Optional[Process]:
        """
        Get the next process based on shortest burst time
        
        Returns:
            Process: Ready process with shortest burst time, or None if no process is ready
        """
        ready_processes = [p for p in self.processes if p.state == ProcessState.READY]
        if not ready_processes:
            return None
            
        # Select process with shortest remaining time
        return min(ready_processes, key=lambda p: p.burst_time)
    
    def run(self) -> None:
        """Run the SJF scheduling simulation"""
        while not self.is_all_completed():
            self.update_process_states()
            
            if self.current_process is None:
                self.current_process = self.get_next_process()
                
                if self.current_process:
                    self.current_process.update_state(ProcessState.RUNNING)
                    if self.current_process.start_time is None:
                        self.current_process.start_time = self.current_time
            
            if self.current_process:
                time_used = self.current_process.execute(1)
                
                if self.current_process.is_completed():
                    self.current_process.completion_time = self.current_time
                    self.current_process.turnaround_time = (
                        self.current_time - self.current_process.arrival_time
                    )
                    self.current_process = None
            
            self.update_waiting_times()
            self.current_time += 1