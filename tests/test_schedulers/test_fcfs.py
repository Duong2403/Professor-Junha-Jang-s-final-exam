# tests/test_schedulers/test_fcfs.py
import pytest
from src.process.process import Process
from src.schedulers.fcfs import FCFSScheduler

def test_fcfs_basic_scheduling():
    """Test basic FCFS scheduling functionality"""
    scheduler = FCFSScheduler()
    
    # Create test processes
    p1 = Process(pid=1, arrival_time=0, burst_time=3)
    p2 = Process(pid=2, arrival_time=1, burst_time=2)
    
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    
    # Run scheduler
    scheduler.run()
    
    # Verify execution order
    assert p1.completion_time < p2.completion_time
    assert p1.turnaround_time == 3  # burst_time
    assert p2.turnaround_time == 4  # wait_time + burst_time

def test_fcfs_process_metrics():
    """Test if process metrics are calculated correctly"""
    scheduler = FCFSScheduler()
    
    p1 = Process(pid=1, arrival_time=0, burst_time=4)
    scheduler.add_process(p1)
    
    scheduler.run()
    
    assert p1.waiting_time == 0
    assert p1.turnaround_time == 4
    assert p1.completion_time == 4