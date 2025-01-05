# examples/basic_usage.py
from src.schedulers.fcfs import FCFSScheduler
from src.process.process import Process
from src.visualization.gantt import GanttChart
from src.utils.metrics import SchedulingMetrics
from src.utils.logger import SchedulerLogger

def main():
    # 1. Khởi tạo logger để theo dõi quá trình chạy
    logger = SchedulerLogger(log_file="scheduler.log")
    
    # 2. Tạo scheduler và thêm các process
    scheduler = FCFSScheduler()
    
    # Thêm một số process mẫu
    processes = [
        Process(pid=1, arrival_time=0, burst_time=5),
        Process(pid=2, arrival_time=2, burst_time=3),
        Process(pid=3, arrival_time=4, burst_time=4)
    ]
    
    for process in processes:
        scheduler.add_process(process)
    
    # 3. Chạy scheduler
    logger.log_scheduler_event("START", "Starting FCFS scheduling")
    scheduler.run()
    logger.log_scheduler_event("END", "Completed FCFS scheduling")
    
    # 4. Tạo biểu đồ Gantt
    chart = GanttChart(scheduler.processes)
    chart.create_chart("schedule.png")  # Lưu biểu đồ thành file schedule.png
    
    # 5. Tính toán và in metrics
    metrics = SchedulingMetrics.calculate_metrics(scheduler.processes)
    logger.log_performance_metrics(metrics)
    
    # 6. Tạo và in báo cáo chi tiết
    report = SchedulingMetrics.generate_report(scheduler.processes)
    print(report)

if __name__ == "__main__":
    main()