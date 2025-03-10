import threading
import time
import uuid
from typing import Callable, Any, Dict, List, Optional

class TaskScheduler:
    """
    A simple scheduler for automation tasks.
    """

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.lock = threading.Lock()
        self.notification_config: Optional[Dict[str, Any]] = None

    def _convert_to_seconds(self, interval: int, unit: str) -> int:
        """
        Convert the interval to seconds based on the unit.
        Valid units are 'seconds', 'minutes', 'hours', and 'days'.
        """
        unit = unit.lower()
        allowed_units = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
        if unit not in allowed_units:
            raise ValueError(f"Invalid unit for interval. Choose from: {list(allowed_units.keys())}")
        return interval * allowed_units[unit]

    def _run_task(self, task_id: str):
        with self.lock:
            task = self.tasks.get(task_id)
            if not task or task.get("cancelled"):
                return

        # Execute the task function
        try:
            task["last_run"] = time.time()
            result = task["function"](*task["args"], **task["kwargs"])
            task["last_result"] = result
            task["status"] = "completed"
            # Optionally notify if configured
            if self.notification_config:
                self._notify(task_id, result)
        except Exception as e:
            task["last_error"] = str(e)
            task["status"] = "error"

        # Reschedule the task if still running and not cancelled
        with self.lock:
            if self.running and not task.get("cancelled"):
                task["next_run"] = time.time() + task["interval"]
                timer = threading.Timer(task["interval"], self._run_task, args=[task_id])
                task["timer"] = timer
                timer.start()

    def schedule_task(
        self,
        function: Callable,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        interval: int = 60,
        unit: str = "seconds"
    ) -> str:
        """
        Schedules a generic task to run repeatedly at the specified interval.
        Returns a unique task ID.
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        seconds = self._convert_to_seconds(interval, unit)
        task_id = str(uuid.uuid4())
        with self.lock:
            timer = threading.Timer(seconds, self._run_task, args=[task_id])
            task_data = {
                "id": task_id,
                "function": function,
                "args": args,
                "kwargs": kwargs,
                "interval": seconds,
                "unit": unit,
                "timer": timer,
                "status": "scheduled",
                "last_run": None,
                "next_run": time.time() + seconds,
                "last_result": None,
                "last_error": None,
                "cancelled": False
            }
            self.tasks[task_id] = task_data
            if self.running:
                timer.start()
        return task_id

    def schedule_search(
        self, url: str, desync_client: Any, interval: int = 60, unit: str = "seconds"
    ) -> str:
        """
        Schedules a single URL search task using the provided DesyncClient.
        """
        def task_function():
            return desync_client.search(url)
        return self.schedule_task(task_function, interval=interval, unit=unit)

    def schedule_bulk_search(
        self, urls: List[str], desync_client: Any, interval: int = 60, unit: str = "seconds"
    ) -> str:
        """
        Schedules a bulk search task for a list of URLs using the DesyncClient.
        """
        def task_function():
            bulk_info = desync_client.bulk_search(target_list=urls)
            bulk_search_id = bulk_info.get("bulk_search_id")
            return desync_client.collect_results(
                bulk_search_id=bulk_search_id, target_links=urls
            )
        return self.schedule_task(task_function, interval=interval, unit=unit)

    def schedule_crawl(
        self, start_url: str, max_depth: int, desync_client: Any, interval: int = 60, unit: str = "seconds"
    ) -> str:
        """
        Schedules a crawl task starting from the given URL with the specified max_depth.
        """
        def task_function():
            return desync_client.crawl(start_url=start_url, max_depth=max_depth)
        return self.schedule_task(task_function, interval=interval, unit=unit)

    def list_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all scheduled tasks with their metadata.
        """
        with self.lock:
            return list(self.tasks.values())

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns the current status of the task identified by task_id.
        """
        with self.lock:
            return self.tasks.get(task_id)

    def cancel_task(self, task_id: str):
        """
        Cancels a scheduled task, preventing further execution.
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                task["cancelled"] = True
                if task.get("timer"):
                    task["timer"].cancel()
                task["status"] = "cancelled"

    def update_task(self, task_id: str, new_interval: int, unit: str = "seconds"):
        """
        Updates the interval for an existing scheduled task.
        """
        seconds = self._convert_to_seconds(new_interval, unit)
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                if task.get("timer"):
                    task["timer"].cancel()
                task["interval"] = seconds
                task["unit"] = unit
                task["next_run"] = time.time() + seconds
                timer = threading.Timer(seconds, self._run_task, args=[task_id])
                task["timer"] = timer
                timer.start()

    def run_now(self, task_id: str):
        """
        Immediately triggers a scheduled task.
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if task and not task.get("cancelled"):
                if task.get("timer"):
                    task["timer"].cancel()
                threading.Thread(target=self._run_task, args=(task_id,)).start()

    def configure_notifications(self, recipient: str, conditions: Dict[str, Any]):
        """
        Configures notifications to alert the recipient when task events occur.
        """
        self.notification_config = {
            "recipient": recipient,
            "conditions": conditions
        }

    def _notify(self, task_id: str, result: Any):
        """
        Internal method to send a notification.
        (This is a placeholder for integrating with an actual notification system.)
        """
        print(f"Notification: Task {task_id} completed with result: {result}")

    def start_scheduler(self):
        """
        Starts the scheduler; tasks scheduled will begin running.
        """
        with self.lock:
            if not self.running:
                self.running = True
                # Start timers for tasks that are not cancelled
                for task in self.tasks.values():
                    if not task.get("cancelled") and (not task.get("timer") or not task["timer"].is_alive()):
                        remaining = max(0, task["next_run"] - time.time())
                        timer = threading.Timer(remaining, self._run_task, args=[task["id"]])
                        task["timer"] = timer
                        timer.start()

    def stop_scheduler(self):
        """
        Stops the scheduler and cancels all running tasks.
        """
        with self.lock:
            self.running = False
            for task in self.tasks.values():
                if task.get("timer"):
                    task["timer"].cancel()
