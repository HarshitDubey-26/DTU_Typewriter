"""Background thread that processes all SQLite operations sequentially.

The main thread NEVER touches the database directly.  It places a DBTask
on the shared queue; this worker picks it up, executes the corresponding
DBOperations method, and puts a Result on the result queue.  The main
thread polls the result queue via root.after().
"""
import threading
import queue
import logging
from app.database.db_operations import DBOperations
from app.workers.task_queue import DBTask, Result

logger = logging.getLogger("dtu_typewriter.db_worker")


class DatabaseWorker(threading.Thread):
    def __init__(self, task_queue: queue.Queue, result_queue: queue.Queue):
        super().__init__(daemon=True, name="db-worker")
        self.task_queue = task_queue
        self.result_queue = result_queue
        self._shutdown = False
        self._next_id = 1

    def run(self) -> None:
        logger.info("DatabaseWorker started")
        db = DBOperations()
        while not self._shutdown:
            try:
                task: DBTask = self.task_queue.get(timeout=0.25)
            except queue.Empty:
                continue

            if task.action == "shutdown":
                logger.info("Shutdown signal received")
                self._shutdown = True
                self.result_queue.put(
                    Result(task_id=task.task_id, data="shutdown")
                )
                break

            try:
                method = getattr(db, task.action)
                data = method(**task.payload)
                self.result_queue.put(
                    Result(
                        task_id=task.task_id,
                        data=data,
                        callback=task.callback,
                    )
                )
            except Exception as exc:
                logger.exception("DB task failed: %s", task.action)
                self.result_queue.put(
                    Result(
                        task_id=task.task_id,
                        error=str(exc),
                        callback=task.callback,
                    )
                )
        db.close()
        logger.info("DatabaseWorker stopped")

    def next_task_id(self) -> int:
        tid = self._next_id
        self._next_id += 1
        return tid
