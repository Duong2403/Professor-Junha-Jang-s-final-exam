# src/schedulers/realtime/earliest_deadline.py
from typing import Optional, Dict
from ..base_scheduler import BaseScheduler
from ...process.process import Process
from ...process.process_state import ProcessState

class EarliestDeadlineFirstScheduler(BaseScheduler):
    """
    Earliest Deadline First (EDF) Scheduler Implementation
    Dynamic priority assignment based on absolute deadlines
    """
    def __init__(self):
        super().__init__()
        self.deadlines: Dict[int, int] = {}  # pid -> absolute deadline
        self.periods: Dict[int, int] = {}    # pid -> period
        
    def add_process(self, process: Process, deadline: int, period: int):
        """
        Add process with its deadline and period
        
        Args:
            process: Process to add
            deadline: Relative deadline
            period: Process period
        """
        self.processes.append(process)
        self.deadlines[process.pid] = process.arrival_time + deadline
        self.periods[process.pid] = period
    
    def update_deadlines(self, pid: int):
        """Update deadline after process completion"""
        if pid in self.deadlines and pid in self.periods:
            self.deadlines[pid] += self.periods[pid]
    
    def get_next_process(self) -> Optional[Process]:
        """Get process with earliest deadline"""
        ready_processes = [
            p for p in self.processes 
            if p.state == ProcessState.READY
        ]
        if not ready_processes:
            return None
        return min(
            ready_processes,
            key=lambda p: self.deadlines[p.pid]
        )
        
    def check_schedulability(self) -> bool:
        """
        Check if task set is schedulable using EDF
        Using processor utilization bound
        """
        if not self.processes:
            return True
            
        utilization = sum(
            p.burst_time / self.periods[p.pid]
            for p in self.processes
        )
        
        return utilization <= 1.0