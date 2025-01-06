# src/utils/metrics.py
from typing import List, Dict
from ..process.process import Process

class SchedulingMetrics:
    """
    Enhanced metrics calculation for scheduler performance
    """
    @staticmethod
    def calculate_metrics(processes: List[Process], total_time: int) -> Dict[str, float]:
        """Calculate scheduling metrics with error handling"""
        try:
            if not processes:
                return {}
                
            # Ensure total_time is at least 1
            total_time = max(1, total_time)
            
            # Calculate totals safely
            total_waiting_time = sum(p.waiting_time for p in processes)
            total_turnaround_time = sum(p.turnaround_time for p in processes)
            total_response_time = sum(
                p.start_time - p.arrival_time if p.start_time is not None else 0 
                for p in processes
            )
            total_burst_time = sum(p.burst_time for p in processes)
            total_context_switches = sum(p.context_switches for p in processes)
            
            # Calculate metrics with safe division
            n_processes = max(1, len(processes))  # Avoid division by zero
            
            metrics = {
                "avg_waiting_time": total_waiting_time / n_processes,
                "avg_turnaround_time": total_turnaround_time / n_processes,
                "avg_response_time": total_response_time / n_processes,
                "cpu_utilization": (total_burst_time / total_time) * 100,
                "throughput": len(processes) / total_time,
                "context_switches": total_context_switches
            }
            
            return {k: round(v, 2) for k, v in metrics.items()}
            
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {
                "avg_waiting_time": 0,
                "avg_turnaround_time": 0,
                "avg_response_time": 0,
                "cpu_utilization": 0,
                "throughput": 0,
                "context_switches": 0
            }

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