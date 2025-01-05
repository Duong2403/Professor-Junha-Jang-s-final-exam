# tests/test_schedulers/test_mlfq.py
import pytest
from src.schedulers.mlfq import MLFQScheduler
from src.process.process import Process

def test_mlfq_queue_demotion():
    """Test process demotion in MLFQ"""
    scheduler = MLFQScheduler(num_queues=3, base_quantum=2)
    
    p1 = Process(pid=1, arrival_time=0, burst_time=6)
    scheduler.add_process(p1)
    scheduler.run()
    
    # Process should have been demoted to lower queues
    assert scheduler.process_queue_map.get(1) is None  # Process completed
    assert p1.turnaround_time > p1.burst_time  # Due to quantum restrictions

def test_mlfq_multiple_processes():
    """Test MLFQ with multiple processes"""
    scheduler = MLFQScheduler()
    
    processes = [
        Process(pid=1, arrival_time=0, burst_time=3),
        Process(pid=2, arrival_time=0, burst_time=4),
        Process(pid=3, arrival_time=0, burst_time=2)
    ]
    
    for p in processes:
        scheduler.add_process(p)
    
    scheduler.run()
    
    # Verify all processes completed
    assert all(p.is_completed() for p in processes)