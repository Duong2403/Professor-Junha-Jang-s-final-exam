# src/schedulers/realtime/rate_monotonic.py
from typing import Optional, List
from ..base_scheduler import BaseScheduler
from ...process.process import Process
from ...process.process_state import ProcessState

class RateMonotonicScheduler(BaseScheduler):
    """
    Rate Monotonic Scheduler for real-time systems
    Assigns priorities based on process periods (shorter period = higher priority)
    """
    
    def __init__(self):
        super().__init__()
        self.process_periods: dict = {}  # pid -> period
    
    def add_process(self, process: Process, period: int) -> None:
        """
        Add new process with its period
        
        Args:
            process: Process to be scheduled
            period: Time period for process execution
        """
        self.processes.append(process)
        self.process_periods[process.pid] = period
        # Assign priority based on period (shorter period = higher priority)
        process.priority = period
    
    def get_next_process(self) -> Optional[Process]:
        """Get highest priority (shortest period) ready process"""
        ready_processes = [p for p in self.processes if p.state == ProcessState.READY]
        if not ready_processes:
            return None
        return min(ready_processes, key=lambda p: self.process_periods[p.pid])
    
    def run(self) -> None:
        """Run Rate Monotonic scheduling simulation"""
        while not self.is_all_completed():
            self.update_process_states()
            
            # Preemption check
            if self.current_process:
                next_process = self.get_next_process()
                if (next_process and 
                    self.process_periods[next_process.pid] < 
                    self.process_periods[self.current_process.pid]):
                    self.current_process.update_state(ProcessState.READY)
                    self.current_process = None
            
            if self.current_process is None:
                self.current_process = self.get_next_process()
                if self.current_process:
                    self.current_process.update_state(ProcessState.RUNNING)
                    if self.current_process.start_time is None:
                        self.current_process.start_time = self.current_time
            
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