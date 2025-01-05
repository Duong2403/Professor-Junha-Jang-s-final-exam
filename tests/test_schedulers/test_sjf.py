# tests/test_schedulers/test_sjf.py
import pytest
from src.process.process import Process
from src.schedulers.sjf import SJFScheduler

def test_sjf_basic_scheduling():
    """Test basic SJF scheduling functionality"""
    scheduler = SJFScheduler()
    
    # Create test processes with different burst times
    p1 = Process(pid=1, arrival_time=0, burst_time=4)
    p2 = Process(pid=2, arrival_time=0, burst_time=2)
    
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    
    scheduler.run()
    
    # Verify shorter job completed first
    assert p2.completion_time < p1.completion_time

def test_sjf_arrival_time_handling():
    """Test SJF handling of different arrival times"""
    scheduler = SJFScheduler()
    
    p1 = Process(pid=1, arrival_time=0, burst_time=4)
    p2 = Process(pid=2, arrival_time=3, burst_time=1)
    
    scheduler.add_process(p1)
    scheduler.add_process(p2)
    
    scheduler.run()
    
    # First process should complete before second arrives
    assert p1.completion_time < p2.start_time