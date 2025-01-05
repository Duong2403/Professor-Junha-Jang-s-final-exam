# tests/test_schedulers/test_realtime.py
import pytest
from src.schedulers.realtime.rate_monotonic import RateMonotonicScheduler
from src.schedulers.realtime.earliest_deadline import EarliestDeadlineFirstScheduler
from src.process.process import Process

def test_rms_schedulability():
    scheduler = RateMonotonicScheduler()
    
    # Create test processes
    p1 = Process(pid=1, arrival_time=0, burst_time=2)
    p2 = Process(pid=2, arrival_time=0, burst_time=3)
    
    # Add processes with periods
    scheduler.add_process(p1, period=5)  # 40% utilization
    scheduler.add_process(p2, period=10) # 30% utilization
    
    # Total utilization 70% should be schedulable
    assert scheduler.check_schedulability() == True

def test_edf_schedulability():
    scheduler = EarliestDeadlineFirstScheduler()
    
    p1 = Process(pid=1, arrival_time=0, burst_time=3)
    p2 = Process(pid=2, arrival_time=0, burst_time=4)
    
    # Add processes with deadlines and periods
    scheduler.add_process(p1, deadline=7, period=7)
    scheduler.add_process(p2, deadline=10, period=10)
    
    # Total utilization 82.8% should be schedulable under EDF
    assert scheduler.check_schedulability() == True