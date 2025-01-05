# tests/test_schedulers/test_priority.py
import pytest
from src.schedulers.priority import PriorityScheduler
from src.process.process import Process

def test_priority_basic():
    """Test basic priority scheduling functionality"""
    scheduler = PriorityScheduler(preemptive=True)
    
    # Create processes with different priorities
    p1 = Process(pid=1, arrival_time=0, burst_time=3, priority=3)
    p2 = Process(pid=2, arrival_time=1, burst_time=2, priority=1)
    
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    scheduler.run()
    
    # p2 should complete before p1 due to higher priority
    assert p2.completion_time < p1.completion_time

def test_priority_preemption():
    """Test priority preemption"""
    scheduler = PriorityScheduler(preemptive=True)
    
    p1 = Process(pid=1, arrival_time=0, burst_time=4, priority=2)
    p2 = Process(pid=2, arrival_time=1, burst_time=2, priority=1)
    
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    scheduler.run()
    
    # p2 should preempt p1
    assert p2.start_time == 1