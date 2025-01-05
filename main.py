import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.process.process_state import ProcessState  # Thêm dòng này

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from tkinter import ttk, messagebox


from src.process.process import Process
from src.schedulers.fcfs import FCFSScheduler
from src.schedulers.sjf import SJFScheduler
from src.schedulers.round_robin import RoundRobinScheduler
from src.schedulers.priority import PriorityScheduler
from src.schedulers.mlfq import MLFQScheduler
from src.visualization.gantt import GanttChart
from src.utils.metrics import SchedulingMetrics

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        self.processes = []
        self.current_time = 0
        self.simulation_speed = 1.0
        self.is_running = False
        self.setup_gui()

    def setup_gui(self):
   # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel for input and controls 
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel)

        # Input Method Selection Frame
        input_method_frame = ttk.LabelFrame(left_panel, text="Input Method", padding=5)
        input_method_frame.pack(fill=tk.X, padx=5, pady=5)

        self.input_method = tk.StringVar(value="manual")
        ttk.Radiobutton(input_method_frame, text="Manual Input", 
                        variable=self.input_method, value="manual",
                        command=self.show_input_frame).pack(anchor=tk.W)
        ttk.Radiobutton(input_method_frame, text="Random Generation", 
                        variable=self.input_method, value="random", 
                        command=self.show_input_frame).pack(anchor=tk.W)
        ttk.Radiobutton(input_method_frame, text="File Import",
                        variable=self.input_method, value="file",
                        command=self.show_input_frame).pack(anchor=tk.W)

        # Frames for different input methods
        self.manual_frame = ttk.LabelFrame(left_panel, text="Process Details", padding=5)
        self.setup_manual_input()

        self.random_frame = ttk.LabelFrame(left_panel, text="Random Generation", padding=5)
        self.setup_random_input()

        self.file_frame = ttk.LabelFrame(left_panel, text="File Import", padding=5)
        self.setup_file_input()

        # Show default input frame
        self.manual_frame.pack(fill=tk.X, padx=5, pady=5)

        # Scheduler Selection Frame
        scheduler_frame = ttk.LabelFrame(left_panel, text="Scheduler Settings", padding=5)
        scheduler_frame.pack(fill=tk.X, padx=5, pady=5)

        self.scheduler_var = tk.StringVar()
        schedulers = ['FCFS', 'SJF', 'Round Robin', 'Priority', 'MLFQ']
        for scheduler in schedulers:
            ttk.Radiobutton(scheduler_frame, text=scheduler,
                            variable=self.scheduler_var,
                            value=scheduler).pack(anchor=tk.W)

        # Quantum Time Input
        quantum_frame = ttk.Frame(scheduler_frame)
        quantum_frame.pack(fill=tk.X, pady=5)
        ttk.Label(quantum_frame, text="Quantum Time:").pack(side=tk.LEFT)
        self.quantum_var = tk.StringVar(value="2")
        ttk.Entry(quantum_frame, textvariable=self.quantum_var, width=10).pack(side=tk.LEFT, padx=5)

        # Simulation Speed Control
        speed_frame = ttk.LabelFrame(left_panel, text="Simulation Speed", padding=5)
        speed_frame.pack(fill=tk.X, padx=5, pady=5)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.1, to=2.0,
                                    orient=tk.HORIZONTAL, value=1.0,
                                    command=self.update_speed)
        self.speed_scale.pack(fill=tk.X)

        # Control Buttons
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="Start", 
                    command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Pause",
                    command=self.pause_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Reset",
                    command=self.reset_simulation).pack(side=tk.LEFT, padx=5)

        # Right panel with notebook for organized display
        right_panel = ttk.Notebook(main_container)
        main_container.add(right_panel)

        # Process Status tab
        status_frame = ttk.Frame(right_panel)
        right_panel.add(status_frame, text="Process Status")
        self.setup_process_table(status_frame)
        
        # IO Operations in Status tab
        io_section = ttk.Frame(status_frame)
        io_section.pack(fill=tk.X, padx=5, pady=5)
        self.setup_io_operations(io_section)

        # Visualization tab
        viz_frame = ttk.Frame(right_panel)
        right_panel.add(viz_frame, text="Visualization")
        
        # Gantt Chart
        gantt_section = ttk.Frame(viz_frame)
        gantt_section.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.setup_gantt_chart(gantt_section)

        # Metrics below Gantt
        metrics_section = ttk.Frame(viz_frame)
        metrics_section.pack(fill=tk.X, padx=5, pady=5)
        self.setup_metrics_display(metrics_section)

        # Comparison tab
        comparison_frame = ttk.Frame(right_panel)
        right_panel.add(comparison_frame, text="Performance Comparison")
        self.setup_performance_comparison(comparison_frame)

        # Log tab
        log_frame = ttk.Frame(right_panel)
        right_panel.add(log_frame, text="Event Log")
        self.setup_log_display(log_frame)

        # Initial visibility
        self.show_input_frame()

        # Configure weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


        ttk.Button(control_frame, text="Compare All", 
              command=self.compare_all_schedulers).pack(side=tk.LEFT, padx=5)

    def setup_manual_input(self):
        entries = [
            ("Process ID:", "pid_var"),
            ("Arrival Time:", "arrival_var"),
            ("Burst Time:", "burst_var"),
            ("Priority:", "priority_var")
        ]
        
        for i, (label, var_name) in enumerate(entries):
            ttk.Label(self.manual_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
            setattr(self, var_name, tk.StringVar())
            ttk.Entry(self.manual_frame, textvariable=getattr(self, var_name)).grid(
                row=i, column=1, padx=5, pady=2)

        # I/O Operations
        io_frame = ttk.Frame(self.manual_frame)
        io_frame.grid(row=len(entries), column=0, columnspan=2, pady=5)
        
        self.has_io = tk.BooleanVar()
        ttk.Checkbutton(io_frame, text="Has I/O Operations", 
                       variable=self.has_io).pack()

        ttk.Button(self.manual_frame, text="Add Process", 
                  command=self.add_process).grid(row=len(entries)+1, 
                                               column=0, columnspan=2, pady=5)

    def setup_random_input(self):
        entries = [
            ("Number of Processes:", "num_processes_var"),
            ("Max Arrival Time:", "max_arrival_var"),
            ("Max Burst Time:", "max_burst_var"),
            ("Max Priority:", "max_priority_var")
        ]
        
        for i, (label, var_name) in enumerate(entries):
            ttk.Label(self.random_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
            setattr(self, var_name, tk.StringVar(value="5"))
            ttk.Entry(self.random_frame, textvariable=getattr(self, var_name)).grid(
                row=i, column=1, padx=5, pady=2)

        ttk.Button(self.random_frame, text="Generate Processes", 
                  command=self.generate_random_processes).grid(
                      row=len(entries), column=0, columnspan=2, pady=5)

    def setup_file_input(self):
        ttk.Button(self.file_frame, text="Choose File", 
                  command=self.import_from_file).pack(pady=5)
        ttk.Label(self.file_frame, text="Supported formats: CSV, JSON").pack()

    def setup_process_table(self, parent):
        table_frame = ttk.LabelFrame(parent, text="Process Status", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("PID", "Status", "Remaining Time", "Waiting Time")
        self.process_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.process_table.heading(col, text=col)
            self.process_table.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, 
                                command=self.process_table.yview)
        self.process_table.configure(yscrollcommand=scrollbar.set)

        self.process_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_input_frame(self):
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

    def add_process(self):
        try:
            process = Process(
                pid=int(self.pid_var.get()),
                arrival_time=int(self.arrival_var.get()),
                burst_time=int(self.burst_var.get()),
                priority=int(self.priority_var.get())
            )
            self.processes.append(process)
            self.update_process_table()
            self.clear_input_fields()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def clear_input_fields(self):
        """Clear all input fields"""
        self.pid_var.set("")
        self.arrival_var.set("")
        self.burst_var.set("")
        self.priority_var.set("")

    def update_process_table(self):
        """Update the process status table"""
        # Clear existing items
        for item in self.process_table.get_children():
            self.process_table.delete(item)
        
        # Add all processes
        for process in self.processes:
            self.process_table.insert("", "end", values=(
                process.pid,
                process.state.value,
                process.remaining_time,
                process.waiting_time
            ))

    def generate_random_processes(self):
        """Generate random processes based on user input"""
        try:
            num_processes = int(self.num_processes_var.get())
            max_arrival = int(self.max_arrival_var.get())
            max_burst = int(self.max_burst_var.get())
            max_priority = int(self.max_priority_var.get())
            
            for i in range(num_processes):
                process = Process(
                    pid=i+1,
                    arrival_time=random.randint(0, max_arrival),
                    burst_time=random.randint(1, max_burst),
                    priority=random.randint(1, max_priority)
                )
                self.processes.append(process)
            
            self.update_process_table()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def import_from_file(self):
        """Import processes from a file"""
        filename = filedialog.askopenfilename(
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
                messagebox.showerror("Error", "Unsupported file format")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")

    def import_from_csv(self, filename):
        """Import processes from CSV file"""
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                process = Process(
                    pid=int(row['pid']),
                    arrival_time=int(row['arrival_time']),
                    burst_time=int(row['burst_time']),
                    priority=int(row.get('priority', 0))
                )
                self.processes.append(process)
        self.update_process_table()

    def import_from_json(self, filename):
        """Import processes from JSON file"""
        with open(filename, 'r') as file:
            data = json.load(file)
            for item in data:
                process = Process(
                    pid=item['pid'],
                    arrival_time=item['arrival_time'],
                    burst_time=item['burst_time'],
                    priority=item.get('priority', 0)
                )
                self.processes.append(process)
        self.update_process_table()

    def start_simulation(self):
        """Start or resume simulation"""
        if not self.processes:
            messagebox.showwarning("Warning", "Please add processes first")
            return
            
        self.is_running = True
        self.run_simulation()

    def pause_simulation(self):
        """Pause simulation"""
        self.is_running = False

    def reset_simulation(self):
        """Reset simulation to initial state"""
        self.current_time = 0
        self.is_running = False
        self.processes = []
        self.update_process_table()

    def update_speed(self, value):
        """Update simulation speed"""
        self.simulation_speed = float(value)

    def run_simulation(self):
        """Main simulation loop"""
        if not self.is_running:
            return
            
        # Get selected scheduler
        scheduler_type = self.scheduler_var.get()
        if not scheduler_type:
            messagebox.showwarning("Warning", "Please select a scheduler")
            return

        # Create scheduler instance if not exists
        if not hasattr(self, 'current_scheduler'):
            self.current_scheduler = self.create_scheduler(scheduler_type)
            # Add processes to scheduler
            for process in self.processes:
                self.current_scheduler.add_process(process)

        # Handle I/O operations
        self.handle_io_operations(self.current_time)

        # Run one step of simulation
        if self.current_scheduler.run_step():
            # Update displays
            self.update_visualization()
            self.update_io_status()
            
            # Log events
            if self.current_scheduler.current_process:
                self.log_event(
                    f"Process {self.current_scheduler.current_process.pid} is running",
                    "State Change"  # Pass event_type as second argument
                )
                
            # Schedule next update
            delay = int(1000 / self.simulation_speed)
            self.root.after(delay, self.run_simulation)
        else:
            # Simulation completed
            self.is_running = False
            self.log_event("Simulation completed", "General")  # Pass event_type as second argument
            self.update_visualization()
            self.update_io_status()

    def create_scheduler(self, scheduler_type):
        """Create appropriate scheduler instance"""
        try:
            quantum = int(self.quantum_var.get())
            if quantum <= 0:
                raise ValueError("Quantum must be greater than 0.")
        except (ValueError, AttributeError):
            quantum = 2  # Default quantum if invalid input
            print("[WARNING] Invalid quantum value. Using default value: 2")

        # Dictionary mapping scheduler types to their classes
        scheduler_map = {
            "FCFS": FCFSScheduler,
            "SJF": SJFScheduler,
            "Round Robin": lambda: RoundRobinScheduler(time_quantum=quantum),
            "Priority": PriorityScheduler,
            "MLFQ": lambda: MLFQScheduler(time_quantum=quantum)
        }

        # Return the correct scheduler or raise an error
        try:
            return scheduler_map[scheduler_type]()
        except KeyError:
            raise ValueError(f"Invalid scheduler type: {scheduler_type}")



    def setup_gantt_chart(self, parent):
        gantt_frame = ttk.LabelFrame(parent, text="Gantt Chart", padding=5)
        gantt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create figure for Gantt chart
        self.gantt_figure = Figure(figsize=(8, 3))
        self.gantt_canvas = FigureCanvasTkAgg(self.gantt_figure, gantt_frame)
        self.gantt_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize empty Gantt chart
        self.update_gantt_chart()

    def update_gantt_chart(self):
        """Update Gantt chart visualization"""
        self.gantt_figure.clear()
        ax = self.gantt_figure.add_subplot(111)
        
        if not self.processes:
            self.gantt_canvas.draw()
            return
            
        # Create Gantt chart
        y_labels = [f"P{p.pid}" for p in self.processes]
        ax.set_yticks(range(len(self.processes)))
        ax.set_yticklabels(y_labels)
        
        for i, process in enumerate(self.processes):
            if process.start_time is not None:
                # Draw execution bar
                width = process.burst_time - process.remaining_time
                ax.barh(i, width, left=process.start_time, 
                    color=self.get_state_color(process.state))
                
                # Draw waiting time
                if process.waiting_time > 0:
                    ax.barh(i, process.waiting_time, left=process.arrival_time,
                        color='lightgray', alpha=0.5)
        
        ax.set_xlabel("Time")
        ax.grid(True)
        
        self.gantt_canvas.draw()

    def get_state_color(self, state):
        """Get color for process state"""
        colors = {
            'NEW': 'lightblue',
            'READY': 'yellow',
            'RUNNING': 'green',
            'WAITING': 'orange',
            'TERMINATED': 'gray'
        }
        return colors.get(state.value, 'white')

    
    def update_metrics_display(self):
            """Update performance metrics display"""
            if not self.processes:
                self.metrics_text.delete('1.0', tk.END)
                self.metrics_text.insert(tk.END, "No processes to analyze")
                return
            
            # Calculate metrics
            total_wait = sum(p.waiting_time for p in self.processes)
            total_turnaround = sum(p.turnaround_time for p in self.processes)
            num_processes = len(self.processes)
            
            # Format metrics text
            metrics_text = f"""
        Average Waiting Time: {total_wait/num_processes:.2f}
        Average Turnaround Time: {total_turnaround/num_processes:.2f}
        Total Processes: {num_processes}
        Current Time: {self.current_time}
            """
            
            self.metrics_text.delete('1.0', tk.END)
            self.metrics_text.insert(tk.END, metrics_text)

    def setup_log_display(self, parent):
        """Setup enhanced log display"""
        log_frame = ttk.LabelFrame(parent, text="Event Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add filter options
        filter_frame = ttk.Frame(log_frame)
        filter_frame.pack(fill=tk.X, pady=2)
        
        self.log_filter = tk.StringVar(value="ALL")
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        filters = ["ALL", "State Changes", "Context Switches", "I/O Events"]
        for f in filters:
            ttk.Radiobutton(filter_frame, text=f, value=f,
                        variable=self.log_filter,
                        command=self.filter_logs).pack(side=tk.LEFT)
        
        # Log text widget
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure text tags for different event types
        self.log_text.tag_configure('State Change', foreground='blue')
        self.log_text.tag_configure('Context Switch', foreground='red')
        self.log_text.tag_configure('I/O', foreground='green')
        self.log_text.tag_configure('General', foreground='black')

    def log_event(self, message, event_type="General"):
        """
        Add event to log with color coding
        Args:
            message: Message to log
            event_type: Type of event (State Change, Context Switch, I/O, or General)
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message, event_type)
        self.log_text.see(tk.END)

    def filter_logs(self):
        """Filter log entries based on selected type"""
        filter_type = self.log_filter.get()
        # Implementation of log filtering
        content = self.log_text.get("1.0", tk.END)
        self.log_text.delete("1.0", tk.END)
        
        if filter_type == "ALL":
            self.log_text.insert(tk.END, content)
            return
        
        # Split content into lines and filter
        lines = content.split('\n')
        for line in lines:
            if filter_type.upper() in line.upper():
                self.log_text.insert(tk.END, line + '\n')



    def update_visualization(self):
        """Update all visualization components"""
        self.update_process_table()
        self.update_gantt_chart()
        self.update_metrics_display()


    def reset_simulation(self):
        """Reset simulation to initial state"""
        self.current_time = 0
        self.is_running = False
        if hasattr(self, 'current_scheduler'):
            delattr(self, 'current_scheduler')
        # Reset process states
        for process in self.processes:
            process.state = ProcessState.NEW
            process.remaining_time = process.burst_time
            process.waiting_time = 0
            process.turnaround_time = 0
            process.start_time = None
            process.completion_time = None
        self.update_visualization()
        self.log_event("Simulation reset")


    
    def setup_metrics_display(self, parent):
        """Setup performance metrics display"""
        metrics_frame = ttk.LabelFrame(parent, text="Performance Metrics", padding=5)
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # CPU Utilization
        cpu_frame = ttk.Frame(metrics_frame)
        cpu_frame.pack(fill=tk.X, pady=2)
        ttk.Label(cpu_frame, text="CPU Utilization:").pack(side=tk.LEFT)
        self.cpu_utilization = ttk.Label(cpu_frame, text="0%")
        self.cpu_utilization.pack(side=tk.RIGHT)
        
        # Context Switches
        context_frame = ttk.Frame(metrics_frame)
        context_frame.pack(fill=tk.X, pady=2)
        ttk.Label(context_frame, text="Context Switches:").pack(side=tk.LEFT)
        self.context_switches = ttk.Label(context_frame, text="0")
        self.context_switches.pack(side=tk.RIGHT)
        
        # Status Table
        status_frame = ttk.Frame(metrics_frame)
        status_frame.pack(fill=tk.X, pady=2)
        
        # Create table headers
        columns = ("Process", "Waiting Time", "Turnaround Time", "Response Time")
        self.status_table = ttk.Treeview(status_frame, columns=columns, show="headings", height=4)
        for col in columns:
            self.status_table.heading(col, text=col)
            self.status_table.column(col, width=100)
        self.status_table.pack(fill=tk.X)
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_table.yview)
        self.status_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Other metrics text area
        self.metrics_text = tk.Text(metrics_frame, height=4, width=40)
        self.metrics_text.pack(fill=tk.X)

    def update_metrics_display(self):
        """Update all metrics displays"""
        if not self.processes:
            self.metrics_text.delete('1.0', tk.END)
            self.metrics_text.insert(tk.END, "No processes to analyze")
            self.cpu_utilization.config(text="0%")
            self.context_switches.config(text="0")
            # Clear table
            for item in self.status_table.get_children():
                self.status_table.delete(item)
            return
        
        # Calculate metrics
        total_wait = sum(p.waiting_time for p in self.processes)
        total_turnaround = sum(p.turnaround_time for p in self.processes)
        total_context_switches = sum(p.context_switches for p in self.processes)
        total_burst = sum(p.burst_time for p in self.processes)
        
        # Calculate CPU utilization
        if self.current_time > 0:
            cpu_util = (total_burst - sum(p.remaining_time for p in self.processes)) / self.current_time * 100
        else:
            cpu_util = 0
            
        num_processes = len(self.processes)
        
        # Update labels
        self.cpu_utilization.config(text=f"{cpu_util:.1f}%")
        self.context_switches.config(text=str(total_context_switches))
        
        # Update status table
        for item in self.status_table.get_children():
            self.status_table.delete(item)
            
        for process in self.processes:
            response_time = process.start_time - process.arrival_time if process.start_time else "N/A"
            self.status_table.insert("", "end", values=(
                f"P{process.pid}",
                process.waiting_time,
                process.turnaround_time,
                response_time
            ))
        
        # Update metrics text
        metrics_text = f"""
    Average Waiting Time: {total_wait/num_processes:.2f}
    Average Turnaround Time: {total_turnaround/num_processes:.2f}
    Total Processes: {num_processes}
    Current Time: {self.current_time}
        """
        
        self.metrics_text.delete('1.0', tk.END)
        self.metrics_text.insert(tk.END, metrics_text)


    def setup_io_operations(self, parent):
        """Setup I/O operations frame"""
        io_frame = ttk.LabelFrame(parent, text="I/O Operations", padding=5)
        io_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # I/O Controls
        control_frame = ttk.Frame(io_frame)
        control_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(control_frame, text="Start Time:").pack(side=tk.LEFT)
        self.io_start = ttk.Entry(control_frame, width=8)
        self.io_start.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Duration:").pack(side=tk.LEFT)
        self.io_duration = ttk.Entry(control_frame, width=8)
        self.io_duration.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Add I/O", 
                command=self.add_io_operation).pack(side=tk.RIGHT)

        # I/O List
        self.io_list = ttk.Treeview(io_frame, columns=("Start", "Duration", "Status"),
                                height=3, show="headings")
        self.io_list.heading("Start", text="Start Time")
        self.io_list.heading("Duration", text="Duration")
        self.io_list.heading("Status", text="Status")
        self.io_list.pack(fill=tk.X, pady=2)

    def setup_performance_comparison(self, parent):
        """Setup performance comparison chart"""
        comparison_frame = ttk.LabelFrame(parent, text="Performance Comparison", padding=5)
        comparison_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create figure for comparison chart
        self.comparison_figure = Figure(figsize=(6, 4))
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_figure, comparison_frame)
        self.comparison_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_performance_comparison(self):
        """Update performance comparison chart"""
        self.comparison_figure.clear()
        ax = self.comparison_figure.add_subplot(111)
        
        # Collect data for each scheduler type
        schedulers = ['FCFS', 'SJF', 'RR', 'Priority', 'MLFQ']
        metrics = {
            'Waiting Time': [],
            'Turnaround Time': [],
            'CPU Utilization': []
        }
        
        for scheduler in schedulers:
            # Run simulation with each scheduler
            test_scheduler = self.create_scheduler(scheduler)
            for process in self.processes:
                test_scheduler.add_process(Process(
                    pid=process.pid,
                    arrival_time=process.arrival_time,
                    burst_time=process.burst_time,
                    priority=process.priority
                ))
            test_scheduler.run()
            
            # Calculate metrics
            results = SchedulingMetrics.calculate_metrics(
                test_scheduler.processes,
                test_scheduler.current_time
            )
            metrics['Waiting Time'].append(results['avg_waiting_time'])
            metrics['Turnaround Time'].append(results['avg_turnaround_time'])
            metrics['CPU Utilization'].append(results['cpu_utilization'])
        
        # Plot comparison
        x = range(len(schedulers))
        width = 0.25
        
        ax.bar([i - width for i in x], metrics['Waiting Time'], width, 
            label='Avg Waiting Time')
        ax.bar(x, metrics['Turnaround Time'], width,
            label='Avg Turnaround Time')
        ax.bar([i + width for i in x], metrics['CPU Utilization'], width,
            label='CPU Utilization')
        
        ax.set_xticks(x)
        ax.set_xticklabels(schedulers)
        ax.set_ylabel('Time Units / Percentage')
        ax.legend()
        
        self.comparison_canvas.draw()
    

    def add_io_operation(self):
        """Add new I/O operation to selected process"""
        # Check if a process is selected
        selection = self.process_table.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a process first")
            return
        
        try:
            # Get I/O details
            start_time = int(self.io_start.get())
            duration = int(self.io_duration.get())
            
            # Get selected process
            item = self.process_table.item(selection[0])
            pid = int(item['values'][0])  # PID is first column
            
            # Find process object
            process = next((p for p in self.processes if p.pid == pid), None)
            if process:
                # Add I/O operation
                io_op = {"start_time": start_time, "duration": duration, "completed": False}
                if not hasattr(process, 'io_operations'):
                    process.io_operations = []
                process.io_operations.append(io_op)
                
                # Add to I/O list display
                self.io_list.insert("", "end", values=(start_time, duration, "Pending"))
                
                # Clear inputs
                self.io_start.delete(0, tk.END)
                self.io_duration.delete(0, tk.END)
                
                # Log event
                self.log_event(
                    f"Added I/O operation to Process {pid} "
                    f"(Start: {start_time}, Duration: {duration})",
                    "I/O"
                )
            else:
                messagebox.showerror("Error", "Process not found")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for start time and duration")

    def handle_io_operations(self, current_time):
        """Handle I/O operations at current time"""
        for process in self.processes:
            if hasattr(process, 'io_operations'):
                for io_op in process.io_operations:
                    # Start I/O
                    if (not io_op['completed'] and 
                        io_op['start_time'] == current_time and 
                        process.state == ProcessState.RUNNING):
                        process.update_state(ProcessState.WAITING)
                        self.log_event(
                            f"Process {process.pid} started I/O operation",
                            "I/O"
                        )
                    
                    # Complete I/O
                    if (not io_op['completed'] and 
                        io_op['start_time'] + io_op['duration'] == current_time and 
                        process.state == ProcessState.WAITING):
                        io_op['completed'] = True
                        process.update_state(ProcessState.READY)
                        self.log_event(
                            f"Process {process.pid} completed I/O operation",
                            "I/O"
                        )

    def update_io_status(self):
        """Update I/O operations status in display"""
        for item in self.io_list.get_children():
            values = self.io_list.item(item)['values']
            start_time = values[0]
            duration = values[1]
            
            if self.current_time < start_time:
                status = "Pending"
            elif self.current_time < start_time + duration:
                status = "In Progress"
            else:
                status = "Completed"
                
            self.io_list.item(item, values=(start_time, duration, status))
    

    def compare_all_schedulers(self):
        """Compare all scheduling algorithms with current processes"""
        if not self.processes:
            messagebox.showwarning("Warning", "Please add processes first")
            return
            
        # Store original processes
        original_processes = self.processes.copy()
        
        # Create data for comparison
        comparison_data = {}
        schedulers = ['FCFS', 'SJF', 'Round Robin', 'Priority', 'MLFQ']
        
        for scheduler_type in schedulers:
            # Create new scheduler
            scheduler = self.create_scheduler(scheduler_type)
            
            # Run simulation to completion
            while not scheduler.is_all_completed():
                scheduler.run_step()
                
            # Calculate metrics
            metrics = self.calculate_scheduler_metrics(scheduler)
            comparison_data[scheduler_type] = metrics
        
        # Restore original processes
        self.processes = original_processes
        
        # Update comparison chart
        self.update_comparison_chart(comparison_data)
        
        # Show detailed comparison window
        self.show_comparison_details(comparison_data)


    def setup_process_table(self, parent):
        table_frame = ttk.LabelFrame(parent, text="Process Status", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("PID", "Priority", "Status", "Remaining Time", "Waiting Time")
        self.process_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Set column headings and widths
        self.process_table.heading("PID", text="PID")
        self.process_table.heading("Priority", text="Priority")
        self.process_table.heading("Status", text="Status")
        self.process_table.heading("Remaining Time", text="Remaining Time")
        self.process_table.heading("Waiting Time", text="Waiting Time")
        
        # Set column widths
        for col in columns:
            self.process_table.column(col, width=100)

    def update_process_table(self):
        """Update the process status table"""
        for item in self.process_table.get_children():
            self.process_table.delete(item)
        
        for process in self.processes:
            self.process_table.insert("", "end", values=(
                process.pid,
                process.priority,
                process.state.value,
                process.remaining_time,
                process.waiting_time
            ))


    def calculate_scheduler_metrics(self, scheduler):
        """Calculate metrics for a scheduler"""
        total_time = scheduler.current_time
        processes = scheduler.processes
        
        total_waiting = sum(p.waiting_time for p in processes)
        total_turnaround = sum(p.turnaround_time for p in processes)
        total_response = sum(
            (p.start_time - p.arrival_time) for p in processes 
            if p.start_time is not None
        )
        
        num_processes = len(processes)
        
        return {
            'avg_waiting_time': total_waiting / num_processes,
            'avg_turnaround_time': total_turnaround / num_processes,
            'avg_response_time': total_response / num_processes,
            'cpu_utilization': (sum(p.burst_time for p in processes) / total_time * 100) 
                            if total_time > 0 else 0,
            'context_switches': sum(p.context_switches for p in processes)
        }

    def show_comparison_details(self, comparison_data):
        """Show detailed comparison between schedulers"""
        details_window = tk.Toplevel(self.root)
        details_window.title("Scheduler Comparison Details")
        
        # Create table
        columns = ("Scheduler", "Avg Wait", "Avg Turnaround", "CPU Util", "Context Switches")
        tree = ttk.Treeview(details_window, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Add data
        for scheduler, metrics in comparison_data.items():
            tree.insert("", "end", values=(
                scheduler,
                f"{metrics['avg_waiting_time']:.2f}",
                f"{metrics['avg_turnaround_time']:.2f}",
                f"{metrics['cpu_utilization']:.1f}%",
                metrics['context_switches']
            ))
        
        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
def main():
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()