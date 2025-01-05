import logging
from config import Config
from src.process.process import Process
from src.schedulers.fcfs import FCFSScheduler
from src.visualization.gantt import GanttChart
from src.utils.logger import setup_logger

def main():
    # Setup logging
    setup_logger(Config.LOG_LEVEL, Config.LOG_FORMAT, Config.LOG_FILE)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting CPU Scheduler Simulation")
    
    try:
        # Example usage will go here
        pass
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise
        
if __name__ == "__main__":
    main()