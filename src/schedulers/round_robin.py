from typing import Optional
from .base_scheduler import BaseScheduler
from ..process.process import Process
from ..process.process_state import ProcessState

class RoundRobinScheduler(BaseScheduler):
    def __init__(self, time_quantum: int = 2):
        super().__init__()
        self.time_quantum = time_quantum
        self.current_quantum_used = 0
        self.ready_queue = []
        
    def add_process(self, process: Process) -> None:
        self.processes.append(process)
        if process.state == ProcessState.READY:
            self.ready_queue.append(process)
            
    def get_next_process(self) -> Optional[Process]:
        # If ready queue is empty, check for new processes
        if not self.ready_queue:
            for process in self.processes:
                if process.state == ProcessState.READY:
                    self.ready_queue.append(process)
                    
        # Return first process in ready queue
        return self.ready_queue.pop(0) if self.ready_queue else None
        
    def run_step(self) -> bool:
        # Update process states based on arrival time
        self.update_process_states()
        
        # If current process exists, increment quantum used
        if self.current_process:
            self.current_quantum_used += 1
            
            # Check if quantum expired
            if self.current_quantum_used >= self.time_quantum:
                if not self.current_process.is_completed():
                    self.current_process.update_state(ProcessState.READY)
                    self.ready_queue.append(self.current_process)
                self.current_process = None
                self.current_quantum_used = 0
        
        # Get next process if no current process
        if self.current_process is None:
            self.current_process = self.get_next_process()
            if self.current_process:
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time
                self.current_process.update_state(ProcessState.RUNNING)
                self.current_quantum_used = 0
                
        # Execute current process
        if self.current_process:
            # Execute for one time unit
            self.current_process.execute(1)
            
            # Check if process completed
            if self.current_process.is_completed():
                self.current_process.completion_time = self.current_time + 1
                self.current_process.turnaround_time = (
                    self.current_process.completion_time - 
                    self.current_process.arrival_time
                )
                self.completed_processes.append(self.current_process)
                self.current_process = None
                self.current_quantum_used = 0
                
        # Update waiting times and current time
        self.update_waiting_times()
        self.current_time += 1
        
        # Return True if simulation should continue
        return not self.is_all_completed()