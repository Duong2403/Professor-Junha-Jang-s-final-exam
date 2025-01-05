# src/schedulers/fcfs.py
from typing import Optional, List
from .base_scheduler import BaseScheduler
from ..process.process import Process
from ..process.process_state import ProcessState

class FCFSScheduler(BaseScheduler):
    """
    First Come First Served (FCFS) Scheduler Implementation
    """
    
    def add_process(self, process: Process) -> None:
        """Add a new process to the scheduler"""
        self.processes.append(process)
        # Sort processes by arrival time
        self.processes.sort(key=lambda p: p.arrival_time)
    
    def get_next_process(self) -> Optional[Process]:
        """Get the next ready process"""
        for process in self.processes:
            if process.state == ProcessState.READY:
                return process
        return None
    
    def run(self) -> None:
        """Run the FCFS scheduling simulation"""
        while not self.is_all_completed():
            # Update process states based on arrival time
            self.update_process_states()
            
            # If no process is running, get next one
            if self.current_process is None:
                self.current_process = self.get_next_process()
                
                if self.current_process:
                    self.current_process.update_state(ProcessState.RUNNING)
                    if self.current_process.start_time is None:
                        self.current_process.start_time = self.current_time
            
            # Execute current process
            if self.current_process:
                # Execute for one time unit
                self.current_process.execute(1)
                
                # Check if process completed
                if self.current_process.is_completed():
                    self.current_process.completion_time = self.current_time + 1  # Add 1 because we just used this time unit
                    # Calculate turnaround time: completion time - arrival time
                    self.current_process.turnaround_time = (
                        self.current_process.completion_time - 
                        self.current_process.arrival_time
                    )
                    self.current_process = None
            
            # Update waiting times and advance clock
            self.update_waiting_times()
            self.current_time += 1