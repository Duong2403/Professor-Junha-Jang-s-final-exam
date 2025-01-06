# src/schedulers/base_scheduler.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ..process.process import Process
from ..process.process_state import ProcessState

class BaseScheduler(ABC):
    """Abstract base class for CPU scheduling algorithms"""
    
    def __init__(self):
        self.current_time: int = 0
        self.processes: List[Process] = []
        self.current_process: Optional[Process] = None
        self.completed_processes: List[Process] = []
        
    def run_step(self) -> bool:
        """
        Execute one step of the scheduling algorithm
        Returns: True if simulation should continue, False if completed
        """
        self.update_process_states()

        if self.current_process is None:
            self.current_process = self.get_next_process()
            if self.current_process:
                if self.current_process.start_time is None:
                    self.current_process.start_time = self.current_time
                self.current_process.update_state(ProcessState.RUNNING)

        if self.current_process:
            try:
                self.current_process.execute(1)

                if self.current_process.is_completed():
                    self.current_process.completion_time = self.current_time + 1
                    self.current_process.turnaround_time = (
                        self.current_process.completion_time -
                        self.current_process.arrival_time
                    )
                    self.completed_processes.append(self.current_process)
                    self.current_process = None

            except ValueError as e:
                print(f"Error: {e}")

        self.update_waiting_times()
        self.current_time += 1

        return not self.is_all_completed()

    
    @abstractmethod
    def add_process(self, process: Process) -> None:
        """Add a new process to the scheduler"""
        pass
    
    @abstractmethod
    def get_next_process(self) -> Optional[Process]:
        """Select the next process to execute"""
        pass
    
    def update_process_states(self) -> None:
        """Update states of all processes based on arrival time"""
        for process in self.processes:
            if process.arrival_time <= self.current_time:
                if process.state == ProcessState.NEW:
                    process.update_state(ProcessState.READY)
    
    def update_waiting_times(self) -> None:
        """Update waiting time for all ready processes"""
        for process in self.processes:
            if process.state == ProcessState.READY:
                process.waiting_time += 1
    
    def is_all_completed(self) -> bool:
        """Check if all processes have completed execution"""
        return all(p.is_completed() for p in self.processes)