# docs/api/schedulers.md
# CPU Scheduler API Documentation

## Base Scheduler
The base scheduler class that all other schedulers inherit from.

```python
class BaseScheduler:
    def add_process(self, process: Process) -> None:
        """Add a new process to the scheduler queue"""
        
    def run(self) -> None:
        """Run the scheduling simulation"""
        
    def get_next_process(self) -> Optional[Process]:
        """Get the next process to execute"""