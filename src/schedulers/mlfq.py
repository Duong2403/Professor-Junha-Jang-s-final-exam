# src/schedulers/mlfq.py
from typing import List, Optional, Dict
from collections import deque
from .base_scheduler import BaseScheduler
from ..process.process import Process
from ..process.process_state import ProcessState

class MLFQScheduler(BaseScheduler):
    """
    Multi-Level Feedback Queue Scheduler
    Implements multiple priority queues with feedback mechanism
    """
    
    def __init__(self, num_queues: int = 3, base_quantum: int = 2):
        super().__init__()
        self.num_queues = num_queues
        self.base_quantum = base_quantum
        self.queues: List[deque] = [deque() for _ in range(num_queues)]
        self.process_queue_map: Dict[int, int] = {}  # pid -> queue_level
        self.current_quantum_used: int = 0
        self.context_switch_penalty: int = 1  # Thêm penalty khi switch context
        
    def get_quantum(self, queue_level: int) -> int:
        """Get time quantum for given queue level"""
        return self.base_quantum * (2 ** queue_level)
    
    def add_process(self, process: Process) -> None:
        """Add new process to highest priority queue"""
        self.processes.append(process)
        if process.state == ProcessState.NEW:
            process.update_state(ProcessState.READY)
        self.process_queue_map[process.pid] = 0
        if process not in self.queues[0]:
            self.queues[0].append(process)
    
    def demote_process(self, process: Process) -> None:
        """
        Demote process to lower priority queue
        Adds context switch penalty when demoting
        """
        current_level = self.process_queue_map[process.pid]
        if current_level < self.num_queues - 1:
            next_level = current_level + 1
            self.process_queue_map[process.pid] = next_level
            if process not in self.queues[next_level]:
                self.queues[next_level].append(process)
                # Add waiting time for context switch
                process.waiting_time += self.context_switch_penalty
        else:
            if process not in self.queues[current_level]:
                self.queues[current_level].append(process)
                process.waiting_time += self.context_switch_penalty
    
    def get_next_process(self) -> Optional[Process]:
        """Get next process from highest non-empty queue"""
        for level, queue in enumerate(self.queues):
            while queue:
                process = queue[0]
                if not process.is_completed():
                    return process
                queue.popleft()
        return None
        
    def run(self) -> None:
        """Run MLFQ scheduling simulation"""
        while not self.is_all_completed():
            self.update_process_states()
            
            if self.current_process is None:
                self.current_process = self.get_next_process()
                if self.current_process:
                    current_level = self.process_queue_map[self.current_process.pid]
                    self.queues[current_level].popleft()
                    self.current_process.update_state(ProcessState.RUNNING)
                    if self.current_process.start_time is None:
                        self.current_process.start_time = self.current_time
                    self.current_quantum_used = 0
                    # Add context switch overhead
                    self.current_time += self.context_switch_penalty
            
            if self.current_process:
                current_level = self.process_queue_map[self.current_process.pid]
                quantum = self.get_quantum(current_level)
                
                # Execute for one time unit
                time_used = self.current_process.execute(1)
                self.current_quantum_used += 1
                
                if self.current_process.is_completed():
                    self.current_process.completion_time = self.current_time + 1
                    self.current_process.turnaround_time = (
                        self.current_process.completion_time - 
                        self.current_process.arrival_time
                    )
                    if self.current_process.pid in self.process_queue_map:
                        del self.process_queue_map[self.current_process.pid]
                    self.current_process = None
                elif self.current_quantum_used >= quantum:
                    # Process used its quantum, demote it
                    self.current_process.update_state(ProcessState.READY)
                    self.demote_process(self.current_process)
                    self.current_process = None
                    self.current_quantum_used = 0
            
            self.update_waiting_times()
            self.current_time += 1