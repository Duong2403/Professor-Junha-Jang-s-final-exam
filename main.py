import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from src.process.process import Process
from src.process.process_state import ProcessState
from src.schedulers.fcfs import FCFSScheduler
from src.schedulers.sjf import SJFScheduler
from src.schedulers.round_robin import RoundRobinScheduler
from src.schedulers.priority import PriorityScheduler
from src.schedulers.mlfq import MLFQScheduler
from src.visualization.gantt import GanttChart
from src.utils.metrics import SchedulingMetrics
from src.interrupt.timer import TimerInterrupt
from src.process.process import Process
from src.process.process_state import ProcessState
# Import cho Rate Monotonic Scheduler
from src.schedulers.realtime.rate_monotonic import RateMonotonicScheduler

# Import cho Earliest Deadline First Scheduler
from src.schedulers.realtime.earliest_deadline import EarliestDeadlineFirstScheduler

class CPUSchedulerGUI:
    def __init__(self, root):
        """Initialize the CPU Scheduler GUI"""
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        
        # Initialize basic attributes
        self.processes = []
        self.current_time = 0
        self.simulation_speed = 1.0
        self.is_running = False
        self.timer_interrupt = None
        
        # Initialize UI variables
        self.scheduler_var = tk.StringVar()
        self.quantum_var = tk.StringVar(value="2")
        self.context_switch_var = tk.StringVar(value="1")
        
        # Create GUI
        self.setup_gui()
            
    def setup_gui(self):
        """Initialize the GUI components in optimized order"""
        # 1. Create main container first
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 2. Create left and right panels
        left_panel = ttk.Frame(self.main_container)
        right_panel = ttk.Notebook(self.main_container)
        
        self.main_container.add(left_panel)
        self.main_container.add(right_panel)
        
        # 3. Set up right panel tabs first (since they contain core components)
        # Status tab
        status_frame = ttk.Frame(right_panel)
        right_panel.add(status_frame, text="Process Status")
        self.setup_process_table(status_frame)
        
        # Metrics tab
        metrics_frame = ttk.Frame(right_panel)
        right_panel.add(metrics_frame, text="Performance")
        self.setup_metrics_display(metrics_frame)  # Core metrics setup
        
        # Visualization tab
        viz_frame = ttk.Frame(right_panel)
        right_panel.add(viz_frame, text="Visualization")
        self.setup_process_visualization(viz_frame)
        
        # 4. Set up left panel components (which may depend on right panel components)
        # Process creation section
        self.setup_process_input(left_panel)
        
        # Scheduler settings
        self.setup_scheduler_settings(left_panel)
        
        # Simulation controls
        self.setup_simulation_controls(left_panel)
        
        # Help section
        self.setup_scheduler_help(left_panel)
        
        # 5. Create any necessary bindings
        self.create_bindings()
        
        # 6. Final UI updates
        self.update_scheduler_settings()  # Initial UI state
        self.reset_metrics_display()      # Clear metrics displays

    def create_bindings(self):
        """Create necessary event bindings"""
        # Update scheduler description when selection changes
        self.scheduler_var.trace('w', self.update_scheduler_settings)
        
        # Update metrics when simulation speed changes
        self.speed_scale.config(command=self.update_speed)
        
        # Process table selection binding for I/O operations
        self.process_table.bind('<<TreeviewSelect>>', self.on_process_select)
        
        # Window resize handling
        self.root.bind('<Configure>', self.on_window_resize)

    def on_window_resize(self, event):
        """Handle window resize event"""
        # Update Gantt chart size if it exists
        if hasattr(self, 'gantt_figure') and hasattr(self, 'gantt_canvas'):
            self.gantt_figure.set_size_inches(
                event.width / 100,  # Convert pixels to inches
                event.height / 200
            )
            self.gantt_canvas.draw()

    def on_process_select(self, event):
        """Handle process selection in table"""
        selection = self.process_table.selection()
        if selection and hasattr(self, 'io_frame'):
            # Enable I/O controls only when a process is selected
            for child in self.io_frame.winfo_children():
                child.configure(state='normal')
        else:
            for child in self.io_frame.winfo_children():
                child.configure(state='disabled')



    def generate_final_report(self):
        """Generate comprehensive final report with error handling"""
        try:
            # Ensure total_time is not zero
            total_time = max(1, self.current_time)  # Use at least 1 for division
            
            report = SchedulingMetrics.generate_report(
                self.processes,
                total_time
            )
            
            # Show report in new window
            report_window = tk.Toplevel(self.root)
            report_window.title("Simulation Results")
            
            # Add report text
            text_widget = tk.Text(report_window, wrap=tk.WORD, width=60, height=20)
            text_widget.insert(tk.END, report)
            text_widget.pack(padx=10, pady=10)
            
            # Add save button
            ttk.Button(report_window, text="Save Report",
                    command=lambda: self.save_report(report)).pack(pady=5)
                    
        except Exception as e:
            messagebox.showerror("Report Error", f"Error generating report: {str(e)}")


    def calculate_current_metrics(self):
        """Calculate current performance metrics with error handling"""
        try:
            # Ensure total_time is at least 1
            total_time = max(1, self.current_time)
            completed = [p for p in self.processes if p.is_completed()]
            
            # Calculate metrics safely
            total_burst = sum(p.burst_time for p in self.processes)
            total_waiting = sum(p.waiting_time for p in self.processes)
            total_turnaround = sum(
                (p.completion_time - p.arrival_time)
                for p in completed if p.completion_time is not None
            )
            total_response = sum(
                (p.start_time - p.arrival_time)
                for p in self.processes if p.start_time is not None
            )
            total_context_switches = sum(p.context_switches for p in self.processes)
            
            # Calculate averages safely
            n_processes = max(1, len(self.processes))
            n_completed = max(1, len(completed)) if completed else 1
            
            return {
                'cpu_utilization': (total_burst - sum(p.remaining_time for p in self.processes)) / total_time * 100,
                'throughput': len(completed) / total_time,
                'avg_waiting': total_waiting / n_processes,
                'avg_turnaround': total_turnaround / n_completed if completed else 0,
                'avg_response': total_response / n_processes,
                'context_switches': total_context_switches
            }
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {
                'cpu_utilization': 0,
                'throughput': 0,
                'avg_waiting': 0,
                'avg_turnaround': 0,
                'avg_response': 0,
                'context_switches': 0
            }
        

    
        
    def setup_process_input(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Process Creation", padding=5)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input Method Selection
        methods_frame = ttk.Frame(input_frame)
        methods_frame.pack(fill=tk.X)
        
        self.input_method = tk.StringVar(value="manual")
        ttk.Radiobutton(methods_frame, text="Manual Input", 
                       variable=self.input_method, 
                       value="manual",
                       command=self.show_input_frame).pack(side=tk.LEFT)
        ttk.Radiobutton(methods_frame, text="Random Generation",
                       variable=self.input_method,
                       value="random",
                       command=self.show_input_frame).pack(side=tk.LEFT)
        ttk.Radiobutton(methods_frame, text="File Import",
                       variable=self.input_method,
                       value="file",
                       command=self.show_input_frame).pack(side=tk.LEFT)
                       
        # Manual Input Fields
        self.manual_frame = ttk.Frame(input_frame)
        self.setup_manual_input_fields()
        
        # Random Generation Fields
        self.random_frame = ttk.Frame(input_frame)
        self.setup_random_input_fields()
        
        # File Import Fields
        self.file_frame = ttk.Frame(input_frame)
        self.setup_file_input_fields()

    def add_process(self, process: Process, **kwargs) -> None:
        """
        Thêm tiến trình vào scheduler với các tham số cần thiết.

        Args:
            process: Tiến trình cần thêm.
            kwargs: Tham số bổ sung cho các thuật toán đặc biệt.
                - `period`: Chu kỳ của tiến trình (dành cho Rate Monotonic).
                - `deadline`: Deadline của tiến trình (dành cho Earliest Deadline First).
        """
        # Kiểm tra nếu cần thêm tham số 'period' hoặc 'deadline'
        if isinstance(self, RateMonotonicScheduler):
            if 'period' not in kwargs:
                raise ValueError("Rate Monotonic Scheduler yêu cầu tham số 'period'")
            period = kwargs['period']
            self.processes.append(process)
            self.process_periods[process.pid] = period
            # Gán ưu tiên dựa trên chu kỳ
            process.priority = period

        elif isinstance(self, EarliestDeadlineFirstScheduler):
            if 'deadline' not in kwargs or 'period' not in kwargs:
                raise ValueError("Earliest Deadline First Scheduler yêu cầu 'deadline' và 'period'")
            deadline = kwargs['deadline']
            period = kwargs['period']
            self.processes.append(process)
            self.deadlines[process.pid] = process.arrival_time + deadline
            self.periods[process.pid] = period

        else:
            # Dành cho các thuật toán cơ bản (FCFS, SJF, Round Robin, Priority)
            self.processes.append(process)
            if isinstance(self, PriorityScheduler):
                # Nếu là Priority Scheduler, kiểm tra thêm thông tin ưu tiên
                if not hasattr(process, 'priority'):
                    raise ValueError("Priority Scheduler yêu cầu 'priority' cho mỗi tiến trình")


    def setup_manual_input_fields(self):
        fields = [
            ("Process ID:", "pid_var"),
            ("Arrival Time:", "arrival_var"),
            ("Burst Time:", "burst_var"),
            ("Priority:", "priority_var"),
            ("I/O Time:", "io_time_var"),  # New field for I/O operations
            ("I/O Duration:", "io_duration_var")  # New field for I/O duration
        ]
        
        for i, (label, var_name) in enumerate(fields):
            ttk.Label(self.manual_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
            setattr(self, var_name, tk.StringVar())
            ttk.Entry(self.manual_frame, textvariable=getattr(self, var_name)).grid(
                row=i, column=1, padx=5, pady=2)
                
        # Dynamic Priority Option
        self.dynamic_priority = tk.BooleanVar()
        ttk.Checkbutton(self.manual_frame, text="Dynamic Priority",
                       variable=self.dynamic_priority).grid(row=len(fields),
                       column=0, columnspan=2)
                       
        ttk.Button(self.manual_frame, text="Add Process",
                  command=self.add_process).grid(row=len(fields)+1,
                  column=0, columnspan=2, pady=5)
                  
    def setup_scheduler_settings(self, parent):
        """Setup scheduler settings panel with all necessary frames"""
        scheduler_frame = ttk.LabelFrame(parent, text="Advanced Scheduler Settings", padding=5)
        scheduler_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Scheduler Selection
        self.scheduler_var = tk.StringVar()
        schedulers = [
            'FCFS', 'SJF', 'Round Robin', 'Priority (Non-preemptive)',
            'Priority (Preemptive)', 'Multi-Level Queue', 'Rate Monotonic',
            'Earliest Deadline First'
        ]
        
        selection_frame = ttk.Frame(scheduler_frame)
        selection_frame.pack(fill=tk.X, pady=5)
        for scheduler in schedulers:
            ttk.Radiobutton(selection_frame, text=scheduler,
                        variable=self.scheduler_var,
                        value=scheduler).pack(anchor=tk.W)
                        
        # Time Quantum Settings
        self.quantum_frame = ttk.Frame(scheduler_frame)  # Create frame for quantum settings
        ttk.Label(self.quantum_frame, text="Time Quantum:").pack(side=tk.LEFT)
        self.quantum_var = tk.StringVar(value="2")
        ttk.Entry(self.quantum_frame, textvariable=self.quantum_var,
                width=10).pack(side=tk.LEFT, padx=5)
                    
        # Priority Settings
        self.priority_frame = ttk.Frame(scheduler_frame)  # Create frame for priority settings
        ttk.Label(self.priority_frame, text="Priority Range:").pack(side=tk.LEFT)
        self.priority_range_var = tk.StringVar(value="1-10")
        ttk.Entry(self.priority_frame, textvariable=self.priority_range_var,
                width=10).pack(side=tk.LEFT, padx=5)
        
        # Realtime Settings
        self.realtime_frame = ttk.Frame(scheduler_frame)  # Create frame for realtime settings
        ttk.Label(self.realtime_frame, text="Deadline Factor:").pack(side=tk.LEFT)
        self.deadline_factor_var = tk.StringVar(value="1.5")
        ttk.Entry(self.realtime_frame, textvariable=self.deadline_factor_var,
                width=10).pack(side=tk.LEFT, padx=5)
                    
        # Context Switch Settings
        context_frame = ttk.Frame(scheduler_frame)
        context_frame.pack(fill=tk.X, pady=5)
        ttk.Label(context_frame, text="Context Switch Overhead:").pack(side=tk.LEFT)
        self.context_switch_var = tk.StringVar(value="1")
        ttk.Entry(context_frame, textvariable=self.context_switch_var,
                width=10).pack(side=tk.LEFT)
        
        # Advanced Options
        advanced_frame = ttk.LabelFrame(scheduler_frame, text="Advanced Options")
        advanced_frame.pack(fill=tk.X, pady=5)
        
        # Dynamic Priority Option
        self.dynamic_priority = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_frame, text="Enable Dynamic Priority",
                        variable=self.dynamic_priority).pack(anchor=tk.W)
        
        # Aging Option for Priority Scheduling
        self.enable_aging = tk.BooleanVar(value=False)
        ttk.Checkbutton(advanced_frame, text="Enable Priority Aging",
                        variable=self.enable_aging).pack(anchor=tk.W)

    def setup_performance_metrics(self, parent):
        metrics_frame = ttk.LabelFrame(parent, text="Real-time Performance Metrics", padding=5)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # CPU Utilization
        cpu_frame = ttk.Frame(metrics_frame)
        cpu_frame.pack(fill=tk.X, pady=2)
        ttk.Label(cpu_frame, text="CPU Utilization:").pack(side=tk.LEFT)
        self.cpu_utilization = ttk.Label(cpu_frame, text="0%")
        self.cpu_utilization.pack(side=tk.RIGHT)
        
        # Throughput
        throughput_frame = ttk.Frame(metrics_frame)
        throughput_frame.pack(fill=tk.X, pady=2)
        ttk.Label(throughput_frame, text="Throughput:").pack(side=tk.LEFT)
        self.throughput = ttk.Label(throughput_frame, text="0 processes/unit time")
        self.throughput.pack(side=tk.RIGHT)
        
        # Context Switches
        context_frame = ttk.Frame(metrics_frame)
        context_frame.pack(fill=tk.X, pady=2)
        ttk.Label(context_frame, text="Context Switches:").pack(side=tk.LEFT)
        self.context_switches = ttk.Label(context_frame, text="0")
        self.context_switches.pack(side=tk.RIGHT)
        
        # Average Times Table
        columns = ("Metric", "Value")
        self.metrics_table = ttk.Treeview(metrics_frame, columns=columns,
                                        show="headings", height=3)
        for col in columns:
            self.metrics_table.heading(col, text=col)
        self.metrics_table.pack(fill=tk.X, pady=5)

    def setup_process_visualization(self, parent):
        viz_frame = ttk.LabelFrame(parent, text="Process Visualization", padding=5)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Enhanced Gantt Chart
        self.gantt_figure = Figure(figsize=(8, 4))
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_figure, viz_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Process State Timeline
        self.timeline_figure = Figure(figsize=(8, 2))
        self.timeline_canvas = FigureCanvasTkAgg(self.timeline_figure, viz_frame)
        self.timeline_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_visualization(self):
        """Update all visualization components with enhanced features"""
        self.update_gantt_chart()
        self.update_timeline()
        self.update_metrics_display()
        self.update_process_table()
        
    def update_gantt_chart(self):
        """Enhanced Gantt chart with I/O operations and context switches"""
        try:
            self.gantt_figure.clear()
            ax = self.gantt_figure.add_subplot(111)
            
            if not self.processes:
                self.gantt_canvas.draw()
                return
            
            y_positions = range(len(self.processes))
            colors = {
                ProcessState.NEW: '#f0f0f0',      # Light gray
                ProcessState.READY: '#ffd700',     # Gold
                ProcessState.RUNNING: '#32cd32',   # Lime green
                ProcessState.WAITING: '#ff6347',   # Tomato red
                ProcessState.TERMINATED: '#4169e1'  # Royal blue
            }

            # Plot timeline for each process
            for i, process in enumerate(self.processes):
                # Plot execution segments
                if process.start_time is not None:
                    executed_time = process.burst_time - process.remaining_time
                    if executed_time > 0:
                        ax.barh(
                            i, 
                            executed_time,
                            left=process.start_time,
                            color=colors[process.state],
                            alpha=0.8,
                            label=f'P{process.pid}'
                        )
                        
                    # Add text label
                    ax.text(
                        process.start_time + executed_time/2,
                        i,
                        f'P{process.pid}',
                        va='center',
                        ha='center'
                    )

                # Plot I/O operations
                if hasattr(process, 'io_operations'):
                    for io_op in process.io_operations:
                        ax.barh(
                            i,
                            io_op['duration'],
                            left=io_op['start_time'],
                            color='red',
                            alpha=0.3,
                            hatch='//',
                            label='I/O'
                        )

            # Customize chart appearance
            ax.set_yticks(y_positions)
            ax.set_yticklabels([f'P{p.pid}' for p in self.processes])
            ax.set_xlabel('Time')
            ax.set_ylabel('Process')
            ax.set_title('CPU Scheduling Gantt Chart')
            ax.grid(True, axis='x', linestyle='--', alpha=0.7)

            # Add legend only once for each type
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), 
                    loc='upper right', bbox_to_anchor=(1.15, 1))

            self.gantt_figure.tight_layout()
            self.gantt_canvas.draw()
            
        except Exception as e:
            print(f"Error updating Gantt chart: {e}")
            
    def update_timeline(self):
        """Update process state timeline visualization"""
        self.timeline_figure.clear()
        ax = self.timeline_figure.add_subplot(111)
        
        # Timeline visualization code here...
        # Show state changes, interrupts, and I/O events
        
        self.timeline_canvas.draw()

    def run_simulation(self):
        """Enhanced simulation loop with interrupt handling"""
        if not self.is_running:
            return
            
        # Get selected scheduler
        scheduler_type = self.scheduler_var.get()
        if not scheduler_type:
            messagebox.showwarning("Warning", "Please select a scheduler")
            return

        # Create or get current scheduler
        if not hasattr(self, 'current_scheduler'):
            self.current_scheduler = self.create_scheduler(scheduler_type)
            self.setup_timer_interrupt()
            
            # Add processes to scheduler
            for process in self.processes:
                self.current_scheduler.add_process(process)

        # Handle interrupts
        self.handle_timer_interrupt()
        self.handle_io_operations()
        self.handle_priority_interrupt()

        # Run one step of simulation
        if self.current_scheduler.run_step():
            self.update_visualization()
            self.log_event(f"Time {self.current_time}: Execution step completed")
            
            # Schedule next update
            delay = int(1000 / self.simulation_speed)
            self.root.after(delay, self.run_simulation)
        else:
            # Simulation completed
            self.is_running = False
            self.generate_final_report()

    def setup_timer_interrupt(self):
        """Setup timer interrupt for preemptive scheduling"""
        quantum = int(self.quantum_var.get())
        self.timer_interrupt = TimerInterrupt(
            quantum=quantum,
            handler=self.handle_timer_interrupt_callback
        )

    def handle_timer_interrupt_callback(self):
        """Callback for timer interrupt"""
        if self.current_scheduler.current_process:
            self.log_event(
                f"Timer Interrupt: Process {self.current_scheduler.current_process.pid}",
                "Interrupt"
            )
            self.current_scheduler.current_process.update_state(ProcessState.READY)
            self.current_scheduler.current_process = None

    def handle_priority_interrupt(self):
        """Handle priority-based preemption"""
        if isinstance(self.current_scheduler, PriorityScheduler):
            if self.current_scheduler.preemptive:
                highest_priority = self.get_highest_priority_process()
                if (highest_priority and self.current_scheduler.current_process and
                    highest_priority.priority < self.current_scheduler.current_process.priority):
                    self.log_event(
                        f"Priority Interrupt: Process {highest_priority.pid} preempts "
                        f"Process {self.current_scheduler.current_process.pid}",
                        "Interrupt"
                    )
                    self.current_scheduler.current_process.update_state(ProcessState.READY)
                    self.current_scheduler.current_process = None

    def generate_final_report(self):
        """Generate comprehensive final report"""
        report = SchedulingMetrics.generate_report(
            self.processes,
            self.current_time
        )
        
        # Show report in new window
        report_window = tk.Toplevel(self.root)
        report_window.title("Simulation Results")
        
        # Add report text
        text_widget = tk.Text(report_window, wrap=tk.WORD, width=60, height=20)
        text_widget.insert(tk.END, report)
        text_widget.pack(padx=10, pady=10)
        
        # Add save button
        ttk.Button(report_window, text="Save Report",
                  command=lambda: self.save_report(report)).pack(pady=5)

    def compare_all_schedulers(self):
        """So sánh tất cả các thuật toán lập lịch"""
        if not self.processes:
            messagebox.showwarning("Warning", "Vui lòng thêm tiến trình trước.")
            return

        # Lưu các tiến trình gốc
        original_processes = self.processes.copy()

        # Danh sách thuật toán
        schedulers = [
            'FCFS', 'SJF', 'Round Robin', 'Priority (Non-preemptive)',
            'Priority (Preemptive)', 'Multi-Level Queue', 'Rate Monotonic',
            'Earliest Deadline First'
        ]

        comparison_data = {}

        for scheduler_type in schedulers:
            scheduler = self.create_scheduler(scheduler_type)
            processes_copy = self.clone_processes(original_processes)
            if scheduler_type == 'Rate Monotonic':
                # Gán period tạm thời cho Rate Monotonic
                period = 10  # Giá trị mặc định hoặc cần xác định cách lấy giá trị phù hợp
                for process in processes_copy:
                    scheduler.add_process(process, period)
            elif scheduler_type == 'Earliest Deadline First':
                # Gán period và deadline tạm thời cho EDF
                period = 10
                deadline = 8
                for process in processes_copy:
                    scheduler.add_process(process, deadline=deadline, period=period)
            else:
                # Các thuật toán khác không yêu cầu thêm tham số
                for process in processes_copy:
                    scheduler.add_process(process)

            # Chạy mô phỏng
            while not scheduler.is_all_completed():
                scheduler.run_step()

            # Tính toán metrics
            metrics = self.calculate_detailed_metrics(scheduler)
            comparison_data[scheduler_type] = metrics

        # Khôi phục các tiến trình ban đầu
        self.processes = original_processes

        # Hiển thị kết quả
        self.show_detailed_comparison(comparison_data)


    def update_timeline(self):
        """Update process state timeline visualization"""
        try:
            self.timeline_figure.clear()
            ax = self.timeline_figure.add_subplot(111)
            
            if not self.processes:
                self.timeline_canvas.draw()
                return
                
            # Plot state changes
            for i, process in enumerate(self.processes):
                # Plot different states with different colors
                states = {
                    ProcessState.NEW: 'gray',
                    ProcessState.READY: 'yellow',
                    ProcessState.RUNNING: 'green',
                    ProcessState.WAITING: 'red',
                    ProcessState.TERMINATED: 'blue'
                }
                
                # Create timeline
                ax.broken_barh(
                    [(process.arrival_time, self.current_time - process.arrival_time)],
                    (i-0.4, 0.8),
                    facecolors=states[process.state],
                    alpha=0.5
                )
                
                # Add labels
                ax.text(
                    0, i,
                    f'P{process.pid}',
                    ha='right',
                    va='center'
                )
                
            # Customize appearance
            ax.set_ylim(-0.5, len(self.processes)-0.5)
            ax.set_xlabel('Time')
            ax.set_title('Process State Timeline')
            ax.grid(True)
            
            self.timeline_figure.tight_layout()
            self.timeline_canvas.draw()
            
        except Exception as e:
            print(f"Error updating timeline: {e}")
        
    def calculate_detailed_metrics(self, scheduler):
        """Calculate comprehensive performance metrics"""
        processes = scheduler.processes
        total_time = scheduler.current_time
        
        # Basic metrics
        total_waiting = sum(p.waiting_time for p in processes)
        total_turnaround = sum(p.turnaround_time for p in processes)
        total_response = sum(
            (p.start_time - p.arrival_time) for p in processes 
            if p.start_time is not None
        )
        
        # Advanced metrics
        cpu_burst_time = sum(p.burst_time for p in processes)
        io_time = sum(
            sum(io['duration'] for io in getattr(p, 'io_operations', []))
            for p in processes
        )
        
        num_processes = len(processes)
        
        return {
            'avg_waiting_time': total_waiting / num_processes,
            'avg_turnaround_time': total_turnaround / num_processes,
            'avg_response_time': total_response / num_processes,
            'cpu_utilization': (cpu_burst_time / total_time * 100) if total_time > 0 else 0,
            'throughput': num_processes / total_time if total_time > 0 else 0,
            'context_switches': sum(p.context_switches for p in processes),
            'io_utilization': (io_time / total_time * 100) if total_time > 0 else 0
        }
        
    def show_detailed_comparison(self, comparison_data):
        """Show detailed comparison with enhanced visualization"""
        comparison_window = tk.Toplevel(self.root)
        comparison_window.title("Detailed Scheduler Comparison")
        
        # Create notebook for different views
        notebook = ttk.Notebook(comparison_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Table View
        table_frame = ttk.Frame(notebook)
        notebook.add(table_frame, text="Table View")
        self.create_comparison_table(table_frame, comparison_data)
        
        # Chart View
        chart_frame = ttk.Frame(notebook)
        notebook.add(chart_frame, text="Chart View")
        self.create_comparison_charts(chart_frame, comparison_data)
        
        # Analysis View
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Analysis")
        self.create_analysis_view(analysis_frame, comparison_data)
        
    def create_comparison_table(self, parent, data):
        """Create detailed comparison table"""
        columns = (
            "Scheduler", "Avg Wait", "Avg Turnaround", "Avg Response",
            "CPU Util", "Throughput", "Context Switches", "I/O Util"
        )
        
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
            
        # Add data rows
        for scheduler, metrics in data.items():
            tree.insert("", "end", values=(
                scheduler,
                f"{metrics['avg_waiting_time']:.2f}",
                f"{metrics['avg_turnaround_time']:.2f}",
                f"{metrics['avg_response_time']:.2f}",
                f"{metrics['cpu_utilization']:.1f}%",
                f"{metrics['throughput']:.2f}",
                metrics['context_switches'],
                f"{metrics['io_utilization']:.1f}%"
            ))
            
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_comparison_charts(self, parent, data):
        """Create comparative charts"""
        figure = Figure(figsize=(10, 8))
        canvas = FigureCanvasTkAgg(figure, parent)
        
        # Create subplots for different metrics
        gs = figure.add_gridspec(2, 2)
        ax1 = figure.add_subplot(gs[0, 0])  # Times
        ax2 = figure.add_subplot(gs[0, 1])  # Utilization
        ax3 = figure.add_subplot(gs[1, :])  # Overview
        
        schedulers = list(data.keys())
        x = range(len(schedulers))
        width = 0.25
        
        # Plot timing metrics
        waiting_times = [data[s]['avg_waiting_time'] for s in schedulers]
        turnaround_times = [data[s]['avg_turnaround_time'] for s in schedulers]
        response_times = [data[s]['avg_response_time'] for s in schedulers]
        
        ax1.bar([i - width for i in x], waiting_times, width, label='Avg Waiting')
        ax1.bar(x, turnaround_times, width, label='Avg Turnaround')
        ax1.bar([i + width for i in x], response_times, width, label='Avg Response')
        ax1.set_title('Timing Metrics')
        ax1.set_xticks(x)
        ax1.set_xticklabels(schedulers, rotation=45)
        ax1.legend()
        
        # Plot utilization
        cpu_util = [data[s]['cpu_utilization'] for s in schedulers]
        io_util = [data[s]['io_utilization'] for s in schedulers]
        
        ax2.bar(x, cpu_util, width, label='CPU Utilization')
        ax2.bar(x, io_util, width, bottom=cpu_util, label='I/O Utilization')
        ax2.set_title('Resource Utilization')
        ax2.set_xticks(x)
        ax2.set_xticklabels(schedulers, rotation=45)
        ax2.legend()
        
        # Overview chart
        metrics_overview = ['CPU Util', 'Throughput', 'Context Switches']
        colors = ['#2ecc71', '#3498db', '#e74c3c']
        
        for i, metric in enumerate(metrics_overview):
            values = [data[s]['cpu_utilization' if metric == 'CPU Util' else
                          'throughput' if metric == 'Throughput' else
                          'context_switches'] for s in schedulers]
            ax3.plot(schedulers, values, marker='o', label=metric, color=colors[i])
            
        ax3.set_title('Performance Overview')
        ax3.set_xticklabels(schedulers, rotation=45)
        ax3.legend()
        
        figure.tight_layout()
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_analysis_view(self, parent, data):
        """Create detailed analysis view"""
        text_widget = tk.Text(parent, wrap=tk.WORD, width=60, height=20)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add analysis text
        analysis = self.generate_comparison_analysis(data)
        text_widget.insert(tk.END, analysis)
        text_widget.config(state=tk.DISABLED)
        
    def generate_comparison_analysis(self, data):
        """Generate detailed analysis of scheduler comparison"""
        analysis = ["Scheduler Performance Analysis", "=" * 30 + "\n"]
        
        # Find best performer for each metric
        metrics = {
            'avg_waiting_time': ('Average Waiting Time', min),
            'avg_turnaround_time': ('Average Turnaround Time', min),
            'avg_response_time': ('Average Response Time', min),
            'cpu_utilization': ('CPU Utilization', max),
            'throughput': ('Throughput', max)
        }
        
        for metric, (name, func) in metrics.items():
            best_scheduler = max(data.items(), key=lambda x: func(x[1][metric]))[0]
            analysis.append(f"Best {name}: {best_scheduler}")
            
        analysis.append("\nDetailed Analysis:")
        for scheduler, metrics in data.items():
            analysis.extend([
                f"\n{scheduler}:",
                f"  Strengths:",
                f"    - CPU Utilization: {metrics['cpu_utilization']:.1f}%",
                f"    - Throughput: {metrics['throughput']:.2f} processes/unit time",
                f"  Timing Performance:",
                f"    - Average Waiting Time: {metrics['avg_waiting_time']:.2f}",
                f"    - Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}",
                f"    - Average Response Time: {metrics['avg_response_time']:.2f}",
                f"  Resource Usage:",
                f"    - Context Switches: {metrics['context_switches']}",
                f"    - I/O Utilization: {metrics['io_utilization']:.1f}%"
            ])
            
        return "\n".join(analysis)

    def clone_processes(self, processes):
        """Tạo bản sao của danh sách tiến trình"""
        return [Process(
            pid=p.pid,
            arrival_time=p.arrival_time,
            burst_time=p.burst_time,
            priority=p.priority
        ) for p in processes]

    def save_report(self, report_content):
        """Save simulation report to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write(report_content)
            messagebox.showinfo("Success", "Report saved successfully!")
    
    def show_input_frame(self):
        """Show selected input frame and hide others"""
        # Hide all frames first
        self.manual_frame.pack_forget()
        self.random_frame.pack_forget()
        self.file_frame.pack_forget()

        # Show selected frame
        method = self.input_method.get()
        if method == "manual":
            self.manual_frame.pack(fill=tk.X, padx=5, pady=5)
        elif method == "random":
            self.random_frame.pack(fill=tk.X, padx=5, pady=5)
        else:  # file
            self.file_frame.pack(fill=tk.X, padx=5, pady=5)

    def setup_random_input_fields(self):
        """Setup fields for random process generation"""
        fields = [
            ("Number of Processes:", "num_processes_var"),
            ("Max Arrival Time:", "max_arrival_var"),
            ("Max Burst Time:", "max_burst_var"),
            ("Max Priority:", "max_priority_var"),
            ("I/O Probability (%):", "io_prob_var")
        ]
        
        for i, (label, var_name) in enumerate(fields):
            ttk.Label(self.random_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
            setattr(self, var_name, tk.StringVar(value="5"))
            ttk.Entry(self.random_frame, textvariable=getattr(self, var_name)).grid(
                row=i, column=1, padx=5, pady=2)
                
        ttk.Button(self.random_frame, text="Generate Processes",
                  command=self.generate_random_processes).grid(
                      row=len(fields), column=0, columnspan=2, pady=5)

    def setup_file_input_fields(self):
        """Setup file import interface"""
        ttk.Button(self.file_frame, text="Choose File",
                  command=self.import_from_file).pack(pady=5)
        ttk.Label(self.file_frame, text="Supported formats: CSV, JSON").pack()

    def create_right_panel(self):
        """Create right panel with visualization and metrics"""
        right_panel = ttk.Notebook(self.main_container)
        self.main_container.add(right_panel)
        
        # Process Status tab
        status_frame = ttk.Frame(right_panel)
        right_panel.add(status_frame, text="Process Status")
        self.setup_process_table(status_frame)
        
        # Visualization tab
        viz_frame = ttk.Frame(right_panel)
        right_panel.add(viz_frame, text="Visualization")
        self.setup_process_visualization(viz_frame)
        
        # Performance Metrics tab
        metrics_frame = ttk.Frame(right_panel)
        right_panel.add(metrics_frame, text="Performance")
        self.setup_performance_metrics(metrics_frame)

    def setup_simulation_controls(self, parent):
        """Setup simulation control panel with increased speed range"""
        control_frame = ttk.LabelFrame(parent, text="Simulation Controls", padding=5)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Speed Control with increased range
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Speed (x):").pack(side=tk.LEFT)
        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=0.1,
            to=4.0,  # Increased maximum speed to 4x
            orient=tk.HORIZONTAL,
            value=1.0,
            command=self.update_speed
        )
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Current speed label
        self.speed_label = ttk.Label(speed_frame, text="1.0x")
        self.speed_label.pack(side=tk.RIGHT)
        
        def update_speed_label(value):
            self.speed_label.config(text=f"{float(value):.1f}x")
            self.simulation_speed = float(value)
        
        self.speed_scale.config(command=update_speed_label)

    def handle_io_operations(self):
        """Handle I/O operations for current processes"""
        for process in self.processes:
            if hasattr(process, 'io_operations'):
                for io_op in process.io_operations:
                    if not io_op['completed']:
                        # Start I/O operation
                        if (io_op['start_time'] == self.current_time and 
                            process.state == ProcessState.RUNNING):
                            process.update_state(ProcessState.WAITING)
                            self.log_event(f"Process {process.pid} started I/O operation")
                        
                        # Complete I/O operation
                        elif (io_op['start_time'] + io_op['duration'] == self.current_time and
                              process.state == ProcessState.WAITING):
                            io_op['completed'] = True
                            process.update_state(ProcessState.READY)
                            self.log_event(f"Process {process.pid} completed I/O operation")

    def get_highest_priority_process(self):
        """Get the process with highest priority from ready queue"""
        ready_processes = [p for p in self.processes if p.state == ProcessState.READY]
        return min(ready_processes, key=lambda p: p.priority) if ready_processes else None

    def log_event(self, message: str, event_type: str = "General"):
        """Add event to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_message, event_type)
            self.log_text.see(tk.END)


    

    def clear_input_fields(self):
        """Clear all manual input fields"""
        self.pid_var.set("")
        self.arrival_var.set("")
        self.burst_var.set("")
        self.priority_var.set("")
        if hasattr(self, 'io_time_var'):
            self.io_time_var.set("")
        if hasattr(self, 'io_duration_var'):
            self.io_duration_var.set("")

    def update_process_table(self):
        """Update process status table with current processes"""
        # Clear existing items
        for item in self.process_table.get_children():
            self.process_table.delete(item)
        
        # Add all processes
        for process in self.processes:
            self.process_table.insert("", "end", values=(
                process.pid,
                process.priority,
                process.state.value,
                process.remaining_time,
                process.waiting_time,
                "Yes" if hasattr(process, 'io_operations') else "No"
            ))

    def setup_process_table(self, parent):
        """Setup process status display table"""
        table_frame = ttk.LabelFrame(parent, text="Process Status", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create table with scrollbar
        columns = (
            "PID", "Priority", "Status", "Remaining Time", 
            "Waiting Time", "Has I/O"
        )
        self.process_table = ttk.Treeview(
            table_frame, columns=columns, show="headings"
        )
        
        # Configure columns
        for col in columns:
            self.process_table.heading(col, text=col)
            self.process_table.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL,
            command=self.process_table.yview
        )
        self.process_table.configure(yscrollcommand=scrollbar.set)
        
        self.process_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    def generate_random_processes(self):
        """Generate random processes based on input parameters"""
        try:
            num_processes = int(self.num_processes_var.get())
            max_arrival = int(self.max_arrival_var.get())  
            max_burst = int(self.max_burst_var.get())
            max_priority = int(self.max_priority_var.get())
            io_probability = int(self.io_prob_var.get()) if self.io_prob_var.get() else 0

            if num_processes <= 0 or max_arrival < 0 or max_burst <= 0 or max_priority <= 0:
                raise ValueError("Values must be positive numbers")
                
            if not 0 <= io_probability <= 100:
                raise ValueError("I/O probability must be between 0 and 100")
            
            # Clear existing processes
            self.processes.clear()
            
            # Generate new processes
            for i in range(num_processes):
                process = Process(
                    pid=i+1,
                    arrival_time=random.randint(0, max_arrival),
                    burst_time=random.randint(1, max_burst),
                    priority=random.randint(1, max_priority)
                )
                
                # Add random I/O operations
                if random.randint(1, 100) <= io_probability:
                    io_start = random.randint(0, process.burst_time - 1)
                    io_duration = random.randint(1, max_burst // 2)
                    
                    io_op = {
                        'start_time': io_start,
                        'duration': io_duration,
                        'completed': False
                    }
                    
                    process.io_operations = [io_op]
                
                self.processes.append(process)
                
            # Sort processes by arrival time
            self.processes.sort(key=lambda p: p.arrival_time)
            
            # Update display
            self.update_process_table()
            self.log_event(f"Generated {num_processes} random processes")
            
            if io_probability > 0:
                self.log_event(
                    f"Added I/O operations with {io_probability}% probability",
                    "I/O"
                )
                
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            
    def validate_numeric_input(self, text):
        """Validate that input is numeric and positive"""
        if not text:
            return True
        try:
            value = int(text)
            return value >= 0
        except ValueError:
            return False

    def setup_random_input_fields(self):
        """Setup fields for random process generation with validation"""
        fields = [
            ("Number of Processes:", "num_processes_var", "5"),
            ("Max Arrival Time:", "max_arrival_var", "10"),
            ("Max Burst Time:", "max_burst_var", "10"),
            ("Max Priority:", "max_priority_var", "5"),
            ("I/O Probability (%):", "io_prob_var", "20")
        ]
        
        # Validation command
        vcmd = (self.root.register(self.validate_numeric_input), '%P')
        
        for i, (label, var_name, default) in enumerate(fields):
            ttk.Label(self.random_frame, text=label).grid(
                row=i, column=0, padx=5, pady=2, sticky="w"
            )
            
            setattr(self, var_name, tk.StringVar(value=default))
            entry = ttk.Entry(
                self.random_frame,
                textvariable=getattr(self, var_name),
                validate="key",
                validatecommand=vcmd
            )
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
        
        # Advanced Options Frame
        advanced_frame = ttk.LabelFrame(self.random_frame, text="Advanced Options")
        advanced_frame.grid(row=len(fields), column=0, columnspan=2, pady=5, sticky="ew")
        
        # I/O Settings
        self.io_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            advanced_frame,
            text="Enable I/O Operations",
            variable=self.io_enabled
        ).pack(anchor="w", padx=5, pady=2)
        
        # Generate Button
        ttk.Button(
            self.random_frame,
            text="Generate Processes",
            command=self.generate_random_processes
        ).grid(
            row=len(fields)+1,
            column=0,
            columnspan=2,
            pady=10
        )
        
        # Configure grid
        self.random_frame.columnconfigure(1, weight=1)


    def import_from_file(self):
        """Import processes from file (CSV or JSON)"""
        filename = filedialog.askopenfilename(
            title="Import Processes",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
            
        try:
            if filename.endswith('.csv'):
                self.import_from_csv(filename)
            elif filename.endswith('.json'):
                self.import_from_json(filename)
            else:
                raise ValueError("Unsupported file format")
                
            self.log_event(f"Imported processes from {filename}")
            
        except Exception as e:
            messagebox.showerror(
                "Import Error",
                f"Error importing file: {str(e)}"
            )

    def import_from_csv(self, filename: str):
        """Import processes from CSV file"""
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            
            # Validate required fields
            required_fields = {'pid', 'arrival_time', 'burst_time'}
            if not required_fields.issubset(reader.fieldnames):
                missing = required_fields - set(reader.fieldnames)
                raise ValueError(f"Missing required fields: {missing}")
                
            # Clear existing processes
            self.processes.clear()
            
            # Read processes
            for row in reader:
                try:
                    process = Process(
                        pid=int(row['pid']),
                        arrival_time=int(row['arrival_time']),
                        burst_time=int(row['burst_time']),
                        priority=int(row.get('priority', 0))
                    )
                    
                    # Add I/O operations if present
                    if 'io_start' in row and 'io_duration' in row:
                        io_start = int(row['io_start'])
                        io_duration = int(row['io_duration'])
                        if io_start >= 0 and io_duration > 0:
                            process.io_operations = [{
                                'start_time': io_start,
                                'duration': io_duration,
                                'completed': False
                            }]
                    
                    self.processes.append(process)
                    
                except ValueError as e:
                    raise ValueError(f"Invalid data in row {reader.line_num}: {e}")
                    
            # Sort processes by arrival time
            self.processes.sort(key=lambda p: p.arrival_time)
            
            # Update display
            self.update_process_table()
            self.log_event(f"Imported {len(self.processes)} processes from CSV")

    def import_from_json(self, filename: str):
        """Import processes from JSON file"""
        with open(filename, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format")
                
            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of processes")
                
            # Clear existing processes
            self.processes.clear()
            
            # Read processes
            for item in data:
                # Validate required fields
                required_fields = {'pid', 'arrival_time', 'burst_time'}
                if not required_fields.issubset(item.keys()):
                    missing = required_fields - set(item.keys())
                    raise ValueError(f"Missing required fields: {missing}")
                    
                try:
                    process = Process(
                        pid=int(item['pid']),
                        arrival_time=int(item['arrival_time']),
                        burst_time=int(item['burst_time']),
                        priority=int(item.get('priority', 0))
                    )
                    
                    # Add I/O operations if present
                    if 'io_operations' in item:
                        io_ops = item['io_operations']
                        if isinstance(io_ops, list):
                            process.io_operations = [
                                {
                                    'start_time': int(op['start_time']),
                                    'duration': int(op['duration']),
                                    'completed': False
                                }
                                for op in io_ops
                                if 'start_time' in op and 'duration' in op
                            ]
                    
                    self.processes.append(process)
                    
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid data in process {item.get('pid', '?')}: {e}")
                    
            # Sort processes by arrival time
            self.processes.sort(key=lambda p: p.arrival_time)
            
            # Update display
            self.update_process_table()
            self.log_event(f"Imported {len(self.processes)} processes from JSON")

    def setup_file_input_fields(self):
        """Setup file import interface"""
        # File selection button
        ttk.Button(
            self.file_frame,
            text="Choose File",
            command=self.import_from_file
        ).pack(pady=5)
        
        # Format information
        info_frame = ttk.Frame(self.file_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            info_frame,
            text="Supported Formats:",
            font=("TkDefaultFont", 9, "bold")
        ).pack(anchor="w")
        
        # CSV Format info
        ttk.Label(
            info_frame,
            text="CSV: pid,arrival_time,burst_time[,priority,io_start,io_duration]"
        ).pack(anchor="w")
        
        # JSON Format info
        ttk.Label(
            info_frame,
            text="JSON: [{pid,arrival_time,burst_time,priority,io_operations[]}]"
        ).pack(anchor="w")
        
        # Example buttons
        ttk.Button(
            self.file_frame,
            text="Download CSV Template",
            command=lambda: self.save_template('csv')
        ).pack(pady=2)
        
        ttk.Button(
            self.file_frame,
            text="Download JSON Template",
            command=lambda: self.save_template('json')
        ).pack(pady=2)

    def save_template(self, format_type: str):
        """Save template file for import"""
        if format_type == 'csv':
            template = "pid,arrival_time,burst_time,priority,io_start,io_duration\n"
            template += "1,0,5,1,2,2\n"
            template += "2,1,4,2,1,1\n"
            filename = "process_template.csv"
        else:  # json
            template = json.dumps([
                {
                    "pid": 1,
                    "arrival_time": 0,
                    "burst_time": 5,
                    "priority": 1,
                    "io_operations": [
                        {"start_time": 2, "duration": 2}
                    ]
                },
                {
                    "pid": 2,
                    "arrival_time": 1,
                    "burst_time": 4,
                    "priority": 2,
                    "io_operations": [
                        {"start_time": 1, "duration": 1}
                    ]
                }
            ], indent=2)
            filename = "process_template.json"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            initialfile=filename,
            filetypes=[
                (f"{format_type.upper()} files", f"*.{format_type}"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(template)
            messagebox.showinfo(
                "Template Saved",
                f"Template file saved to {filepath}"
            )



    def update_speed(self, value):
        """Update simulation speed"""
        self.simulation_speed = float(value)
        self.log_event(f"Simulation speed updated to {value}x")

    def setup_simulation_controls(self, parent):
        """Setup simulation control panel"""
        control_frame = ttk.LabelFrame(parent, text="Simulation Controls", padding=5)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Speed Control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=0.1,
            to=2.0,
            orient=tk.HORIZONTAL,
            value=1.0,
            command=self.update_speed
        )
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Current speed label
        self.speed_label = ttk.Label(speed_frame, text="1.0x")
        self.speed_label.pack(side=tk.RIGHT)
        
        # Control Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self.start_simulation
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(
            button_frame,
            text="Pause",
            command=self.pause_simulation,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset_simulation
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Compare All",
            command=self.compare_all_schedulers
        ).pack(side=tk.LEFT, padx=5)

    def start_simulation(self):
        """Start or resume simulation"""
        if not self.processes:
            messagebox.showwarning(
                "Warning",
                "Please add processes first"
            )
            return
            
        if not self.scheduler_var.get():
            messagebox.showwarning(
                "Warning",
                "Please select a scheduler"
            )
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.run_simulation()
        
    def pause_simulation(self):
        """Pause simulation"""
        self.is_running = False

        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.log_event("Simulation paused")
        
    def reset_simulation(self):
        """Reset simulation to initial state"""
        # Reset simulation variables
        self.current_time = 0
        self.is_running = False
        
        # Reset scheduler
        if hasattr(self, 'current_scheduler'):
            delattr(self, 'current_scheduler')
        
        # Reset processes to initial state
        for process in self.processes:
            process.state = ProcessState.NEW
            process.remaining_time = process.burst_time
            process.waiting_time = 0
            process.turnaround_time = 0
            process.start_time = None
            process.completion_time = None
            process.context_switches = 0
            if hasattr(process, 'io_operations'):
                for io_op in process.io_operations:
                    io_op['completed'] = False
        
        # Reset UI state
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.speed_scale.set(1.0)
        self.simulation_speed = 1.0
        
        # Update displays
        self.update_process_table()
        if hasattr(self, 'gantt_canvas'):
            self.update_gantt_chart()
        if hasattr(self, 'metrics_display'):
            self.update_metrics_display()
            
        self.log_event("Simulation reset")

    def run_simulation(self):
        """Main simulation loop"""
        if not self.is_running:
            return
        
        # Create or get scheduler
        if not hasattr(self, 'current_scheduler'):
            scheduler_type = self.scheduler_var.get()
            self.current_scheduler = self.create_scheduler(scheduler_type)
            
            # Add processes to scheduler
            for process in self.processes:
                self.current_scheduler.add_process(process)
                
            self.log_event(f"Started {scheduler_type} scheduler")
        
        # Run one simulation step
        if self.current_scheduler.run_step():
            # Update displays
            self.update_visualization()
            
            # Handle I/O operations
            self.handle_io_operations()
            
            # Schedule next update
            delay = int(1000 / self.simulation_speed)
            self.root.after(delay, self.run_simulation)
        else:
            # Simulation completed
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.generate_final_report()
            self.log_event("Simulation completed")


    def create_scheduler(self, scheduler_type: str):
        """
        Tạo đối tượng scheduler phù hợp dựa trên loại đã chọn

        Args:
            scheduler_type: Tên thuật toán lập lịch

        Returns:
            Đối tượng scheduler
        """
        try:
            # Lấy giá trị quantum cho các thuật toán cần
            quantum = int(self.quantum_var.get())
            if quantum <= 0:
                raise ValueError("Quantum phải lớn hơn 0")
            
            # Lấy giá trị context switch overhead
            context_switch = int(self.context_switch_var.get())
            if context_switch < 0:
                raise ValueError("Context switch overhead không thể âm")

            if scheduler_type == 'FCFS':
                scheduler = FCFSScheduler()

            elif scheduler_type == 'SJF':
                scheduler = SJFScheduler()

            elif scheduler_type == 'Round Robin':
                scheduler = RoundRobinScheduler(time_quantum=quantum)

            elif scheduler_type == 'Priority (Non-preemptive)':
                scheduler = PriorityScheduler(preemptive=False)

            elif scheduler_type == 'Priority (Preemptive)':
                scheduler = PriorityScheduler(preemptive=True)

            elif scheduler_type == 'Multi-Level Queue':
                scheduler = MLFQScheduler(
                    num_queues=3,  # Có thể cấu hình
                    base_quantum=quantum
                )

            elif scheduler_type == 'Rate Monotonic':
                scheduler = RateMonotonicScheduler()

            elif scheduler_type == 'Earliest Deadline First':
                scheduler = EarliestDeadlineFirstScheduler()

            else:
                raise ValueError(f"Loại scheduler không hợp lệ: {scheduler_type}")

            # Cấu hình chung nếu có
            for attr in ['context_switch_penalty', 'context_switch_overhead']:
                if hasattr(scheduler, attr):
                    setattr(scheduler, attr, context_switch)

            self.log_event(f"Tạo scheduler {scheduler_type} (Quantum={quantum}, CS={context_switch})")
            return scheduler

        except (ValueError, AttributeError) as e:
            messagebox.showerror(
                "Lỗi tạo scheduler",
                str(e)
            )
            return None


    def get_scheduler_description(self, scheduler_type: str) -> str:
        """Get description of selected scheduler"""
        descriptions = {
            'FCFS': """
                First Come First Served (FCFS)
                - Non-preemptive scheduling
                - Processes run in order of arrival
                - Simple implementation
                - May suffer from convoy effect
            """,
            'SJF': """
                Shortest Job First (SJF)
                - Non-preemptive scheduling
                - Selects process with shortest burst time
                - Optimal for average waiting time
                - Requires knowing/estimating burst times
            """,
            'Round Robin': """
                Round Robin (RR)
                - Preemptive scheduling
                - Each process gets fixed time quantum
                - Fair allocation of CPU
                - Good for time-sharing systems
            """,
            'Priority (Non-preemptive)': """
                Priority Scheduling (Non-preemptive)
                - Processes run based on priority
                - Higher priority processes run first
                - May cause starvation
                - No preemption once started
            """,
            'Priority (Preemptive)': """
                Priority Scheduling (Preemptive)
                - Similar to non-preemptive priority
                - Allows preemption by higher priority
                - Better response for high priority
                - More context switches
            """,
            'Multi-Level Queue': """
                Multi-Level Feedback Queue (MLFQ)
                - Multiple priority queues
                - Dynamic priority adjustment
                - Favors shorter processes
                - Prevents starvation
            """,
            'Rate Monotonic': """
                Rate Monotonic (RM)
                - Real-time scheduling
                - Fixed priorities based on periods
                - Optimal for fixed periodic tasks
                - Requires known periods
            """,
            'Earliest Deadline First': """
                Earliest Deadline First (EDF)
                - Real-time scheduling
                - Dynamic priorities based on deadlines
                - Optimal CPU utilization
                - Requires known deadlines
            """
        }
        
        return descriptions.get(scheduler_type, "No description available.")

    def setup_scheduler_help(self, parent):
        """Setup help information for schedulers"""
        help_frame = ttk.LabelFrame(parent, text="Scheduler Information", padding=5)
        help_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create text widget for description
        self.help_text = tk.Text(help_frame, wrap=tk.WORD, height=6)
        self.help_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Update description when scheduler selected
        def update_description(*args):
            scheduler_type = self.scheduler_var.get()
            if scheduler_type:
                description = self.get_scheduler_description(scheduler_type)
                self.help_text.delete('1.0', tk.END)
                self.help_text.insert('1.0', description)
        
        self.scheduler_var.trace('w', update_description)

    def update_scheduler_settings(self, *args):
        """Update UI based on selected scheduler"""
        scheduler_type = self.scheduler_var.get()
        
        # Show/hide quantum setting
        if scheduler_type in ['Round Robin', 'Multi-Level Queue']:
            self.quantum_frame.pack(fill=tk.X, pady=2)
        else:
            self.quantum_frame.pack_forget()
        
        # Show/hide priority settings
        if 'Priority' in scheduler_type:
            self.priority_frame.pack(fill=tk.X, pady=2)
        else:
            self.priority_frame.pack_forget()
        
        # Show/hide realtime settings
        if scheduler_type in ['Rate Monotonic', 'Earliest Deadline First']:
            self.realtime_frame.pack(fill=tk.X, pady=2)
        else:
            self.realtime_frame.pack_forget()

    def setup_metrics_display(self, parent):
        """Setup the metrics display panel"""
        metrics_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding=5)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Real-time metrics
        self.setup_realtime_metrics(metrics_frame)
        
        # Averages table
        self.setup_averages_table(metrics_frame)
        
        # Process details
        self.setup_process_details(metrics_frame)

    def setup_realtime_metrics(self, parent):
        """Setup real-time metrics display"""
        realtime_frame = ttk.Frame(parent)
        realtime_frame.pack(fill=tk.X, pady=5)
        
        # CPU Utilization
        cpu_frame = ttk.Frame(realtime_frame)
        cpu_frame.pack(fill=tk.X, pady=2)
        ttk.Label(cpu_frame, text="CPU Utilization:").pack(side=tk.LEFT)
        self.cpu_util_label = ttk.Label(cpu_frame, text="0%")
        self.cpu_util_label.pack(side=tk.RIGHT)
        
        # Throughput
        throughput_frame = ttk.Frame(realtime_frame)
        throughput_frame.pack(fill=tk.X, pady=2)
        ttk.Label(throughput_frame, text="Throughput:").pack(side=tk.LEFT)
        self.throughput_label = ttk.Label(throughput_frame, text="0 processes/sec")
        self.throughput_label.pack(side=tk.RIGHT)
        
        # Context Switches
        context_frame = ttk.Frame(realtime_frame)
        context_frame.pack(fill=tk.X, pady=2)
        ttk.Label(context_frame, text="Context Switches:").pack(side=tk.LEFT)
        self.context_switch_label = ttk.Label(context_frame, text="0")
        self.context_switch_label.pack(side=tk.RIGHT)

    def setup_averages_table(self, parent):
        """Setup table for average metrics"""
        averages_frame = ttk.Frame(parent)
        averages_frame.pack(fill=tk.X, pady=5)
        
        columns = ("Metric", "Value")
        self.averages_table = ttk.Treeview(
            averages_frame,
            columns=columns,
            show="headings",
            height=3
        )
        
        for col in columns:
            self.averages_table.heading(col, text=col)
            self.averages_table.column(col, width=150)
        
        self.averages_table.pack(fill=tk.X)

    def setup_process_details(self, parent):
        """Setup detailed process metrics table"""
        details_frame = ttk.Frame(parent)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = (
            "PID",
            "Burst Time",
            "Waiting Time",
            "Turnaround Time",
            "Response Time"
        )
        self.details_table = ttk.Treeview(
            details_frame,
            columns=columns,
            show="headings",
            height=5
        )
        
        for col in columns:
            self.details_table.heading(col, text=col)
            self.details_table.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(
            details_frame,
            orient=tk.VERTICAL,
            command=self.details_table.yview
        )
        self.details_table.configure(yscrollcommand=scrollbar.set)
        
        self.details_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_metrics_display(self):
        """Cập nhật tất cả các số liệu hiệu năng"""
        if not self.processes:
            self.reset_metrics_display()
            return

        # Tính toán các số liệu hiệu năng
        metrics = self.calculate_current_metrics()

        # Cập nhật nhãn hiển thị hiệu năng
        self.cpu_util_label.config(
            text=f"{metrics['cpu_utilization']:.1f}%"  # Hiển thị giá trị CPU chuẩn hóa
        )
        self.throughput_label.config(
            text=f"{metrics['throughput']:.2f} processes/sec"
        )
        self.context_switch_label.config(
            text=str(metrics['context_switches'])
        )

        # Cập nhật bảng số liệu trung bình
        self.update_averages_table(metrics)

        # Cập nhật bảng chi tiết tiến trình
        self.update_process_details()


    def calculate_current_metrics(self):
        """Calculate current performance metrics"""
        total_time = self.current_time if self.current_time > 0 else 1
        completed = [p for p in self.processes if p.is_completed()]
        
        # Calculate metrics
        total_burst = sum(p.burst_time for p in self.processes)
        total_waiting = sum(p.waiting_time for p in self.processes)
        total_turnaround = sum(
            (p.completion_time - p.arrival_time)
            for p in completed if p.completion_time is not None
        )
        total_response = sum(
            (p.start_time - p.arrival_time)
            for p in self.processes if p.start_time is not None
        )
        total_context_switches = sum(p.context_switches for p in self.processes)
        
        # Calculate averages
        n_processes = len(self.processes)
        n_completed = len(completed)
        
        return {
            'cpu_utilization': (total_burst - sum(p.remaining_time for p in self.processes)) / total_time * 100,
            'throughput': n_completed / total_time if n_completed > 0 else 0,
            'avg_waiting': total_waiting / n_processes if n_processes > 0 else 0,
            'avg_turnaround': total_turnaround / n_completed if n_completed > 0 else 0,
            'avg_response': total_response / n_processes if n_processes > 0 else 0,
            'context_switches': total_context_switches
        }

    def update_averages_table(self, metrics):
        """Update the averages metrics table"""
        # Clear current items
        for item in self.averages_table.get_children():
            self.averages_table.delete(item)
        
        # Add metrics
        self.averages_table.insert("", "end", values=(
            "Average Waiting Time",
            f"{metrics['avg_waiting']:.2f}"
        ))
        self.averages_table.insert("", "end", values=(
            "Average Turnaround Time",
            f"{metrics['avg_turnaround']:.2f}"
        ))
        self.averages_table.insert("", "end", values=(
            "Average Response Time",
            f"{metrics['avg_response']:.2f}"
        ))

    def update_process_details(self):
        """Update the process details table"""
        # Clear current items
        for item in self.details_table.get_children():
            self.details_table.delete(item)
        
        # Add process details
        for process in self.processes:
            turnaround_time = (
                process.completion_time - process.arrival_time
                if process.completion_time is not None
                else "-"
            )
            response_time = (
                process.start_time - process.arrival_time
                if process.start_time is not None
                else "-"
            )
            
            self.details_table.insert("", "end", values=(
                process.pid,
                process.burst_time,
                process.waiting_time,
                turnaround_time,
                response_time
            ))

    def reset_metrics_display(self):
        """Reset all metrics displays to initial state"""
        # Reset real-time labels
        self.cpu_util_label.config(text="0%")
        self.throughput_label.config(text="0 processes/sec")
        self.context_switch_label.config(text="0")
        
        # Clear tables
        for table in [self.averages_table, self.details_table]:
            for item in table.get_children():
                table.delete(item)

def main():
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()