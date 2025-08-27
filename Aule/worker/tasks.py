"""
Step 1: simple script placeholder. In Step 2 we can add a task queue (Celery/RQ) and schedule.
Running: `python -m worker.tasks` just validates connectivity.
"""
import os
import time
import sys
from db.sessions import engine


if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        print("[worker] DB connectivity OK")
    except Exception as e:
        print(f"[worker] DB connectivity FAILED: {e}")
        sys.exit(1)


    print("[worker] Idle loop. (Queue coming next step)")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("[worker] Stopped")