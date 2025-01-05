# src/utils/metrics.py
from typing import List, Dict
from ..process.process import Process

class SchedulingMetrics:
    """
    Enhanced metrics calculation for scheduler performance
    """
    @staticmethod
    def calculate_metrics(processes: List[Process], total_time: int) -> Dict[str, float]:
        if not processes:
            return {}
        
        # Basic metrics
        total_waiting_time = sum(p.waiting_time for p in processes)
        total_turnaround_time = sum(p.turnaround_time for p in processes)
        total_response_time = sum(
            p.start_time - p.arrival_time for p in processes 
            if p.start_time is not None
        )
        total_burst_time = sum(p.burst_time for p in processes)
        total_context_switches = sum(p.context_switches for p in processes)
        
        # Calculate metrics
        metrics = {
            "avg_waiting_time": total_waiting_time / len(processes),
            "avg_turnaround_time": total_turnaround_time / len(processes),
            "avg_response_time": total_response_time / len(processes),
            "cpu_utilization": (total_burst_time / total_time) * 100,
            "throughput": len(processes) / total_time,
            "context_switches": total_context_switches
        }
        
        return {k: round(v, 2) for k, v in metrics.items()}

    @staticmethod
    def generate_report(processes: List[Process], total_time: int) -> str:
        """Generate detailed performance report"""
        metrics = SchedulingMetrics.calculate_metrics(processes, total_time)
        
        report = [
            "\nScheduling Performance Report",
            "============================",
            f"Total Processes: {len(processes)}",
            f"Total Time: {total_time}",
            f"Average Waiting Time: {metrics['avg_waiting_time']:.2f}",
            f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}",
            f"Average Response Time: {metrics['avg_response_time']:.2f}",
            f"CPU Utilization: {metrics['cpu_utilization']:.2f}%",
            f"Throughput: {metrics['throughput']:.2f} processes/unit time",
            f"Total Context Switches: {metrics['context_switches']}",
            "\nPer-Process Details:",
            "-------------------"
        ]
        
        for p in processes:
            report.append(
                f"Process {p.pid}:"
                f" Wait={p.waiting_time},"
                f" Turnaround={p.turnaround_time},"
                f" Response={p.start_time - p.arrival_time if p.start_time else 'N/A'},"
                f" Context Switches={p.context_switches}"
            )
            
        return "\n".join(report)