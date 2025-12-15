import logging
from contextlib import contextmanager
from typing import List, Dict, Any

# Global list to store steps for the current test
# This is reset by the `reset_step_history` fixture in conftest.py
current_steps: List[Dict[str, Any]] = []

@contextmanager
def step(name: str):
    """
    Context manager to log a test step and track its status (passed/failed).
    """
    step_info = {"name": name, "status": "running", "error": None}
    # Add to history immediately
    current_steps.append(step_info)
    logging.info(f"STEP START: {name}")
    try:
        yield
        step_info["status"] = "passed"
        logging.info(f"STEP PASS: {name}")
    except Exception as e:
        step_info["status"] = "failed"
        step_info["error"] = str(e)
        logging.error(f"STEP FAIL: {name} - {e}")
        raise
