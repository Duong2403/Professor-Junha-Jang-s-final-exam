# src/visualization/gantt.py
import matplotlib.pyplot as plt
from typing import List, Dict
from ..process.process import Process
from ..process.process_state import ProcessState

class GanttChart:
    """
    Gantt Chart visualization for CPU scheduling
    """
    def __init__(self, processes: List[Process], title: str = "CPU Scheduling Gantt Chart"):
        self.processes = processes
        self.title = title
        self.colors: Dict[ProcessState, str] = {
            ProcessState.RUNNING: "#2ecc71",    # Green
            ProcessState.READY: "#3498db",      # Blue
            ProcessState.WAITING: "#e74c3c",    # Red
            ProcessState.TERMINATED: "#95a5a6",  # Gray
        }

    def _plot_process_timeline(self, ax, process: Process, y_position: int) -> None:
        """
        Plot timeline for a single process
        
        Args:
            ax: Matplotlib axis
            process: Process to plot
            y_position: Vertical position in chart
        """
        # Plot running time
        if process.start_time is not None and process.completion_time is not None:
            ax.barh(
                y_position,
                process.completion_time - process.start_time,
                left=process.start_time,
                color=self.colors[ProcessState.RUNNING],
                alpha=0.5
            )

        # Plot waiting time
        if process.start_time > process.arrival_time:
            ax.barh(
                y_position,
                process.start_time - process.arrival_time,
                left=process.arrival_time,
                color=self.colors[ProcessState.READY],
                alpha=0.5
            )

    def create_chart(self, save_path: str = None) -> None:
        """
        Create and display/save Gantt chart
        
        Args:
            save_path: Optional path to save the chart image
        """
        fig, ax = plt.subplots(figsize=(12, len(self.processes) * 0.5 + 2))
        
        # Plot each process timeline
        for i, process in enumerate(self.processes):
            self._plot_process_timeline(ax, process, i)
        
        # Customize chart appearance
        ax.set_xlabel("Time")
        ax.set_ylabel("Process ID")
        ax.set_yticks(range(len(self.processes)))
        ax.set_yticklabels([f"P{p.pid}" for p in self.processes])
        ax.set_title(self.title)
        ax.grid(True)
        
        # Save or show
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()