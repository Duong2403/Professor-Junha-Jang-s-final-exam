# tests/test_schedulers/test_rr.py
import pytest
from src.process.process import Process
from src.schedulers.round_robin import RoundRobinScheduler

def test_rr_time_quantum():
    """Test if Round Robin respects time quantum"""
    scheduler = RoundRobinScheduler(time_quantum=2)
    
    p1 = Process(pid=1, arrival_time=0, burst_time=4)
    p2 = Process(pid=2, arrival_time=0, burst_time=3)
    
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    
    scheduler.run()
    
    # Both processes should have multiple context switches
    assert p1.completion_time > p1.burst_time
    assert p2.completion_time > p2.burst_time

def test_rr_process_completion():
    """Test if processes complete correctly in RR"""
    scheduler = RoundRobinScheduler(time_quantum=2)
    
    p1 = Process(pid=1, arrival_time=0, burst_time=3)
    
    scheduler.add_process(p1)
    scheduler.run()
    
    assert p1.is_completed()
    assert p1.remaining_time == 0
    assert p1.turnaround_time == 3