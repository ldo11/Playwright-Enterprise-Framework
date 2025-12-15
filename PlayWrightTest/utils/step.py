<<<<<<< HEAD
from contextlib import contextmanager
from typing import List, Dict, Any

# Global list to track steps for the current test execution
# Each item is a dict: {"name": str, "status": "passed"|"failed", "error": str|None}
current_steps: List[Dict[str, Any]] = []

@contextmanager
def step(description: str):
    """
    Context manager to define a test step.
    Prints the step description and statuses.
    Records the step in `current_steps` for reporting.
    If an exception occurs, it annotates the exception message with the step name.
    """
    print(f"\n--- STEP: {description} ---")
    step_record = {"name": description, "status": "running", "error": None}
    current_steps.append(step_record)
    
    try:
        yield
        step_record["status"] = "passed"
        print(f"--- STEP PASSED: {description} ---")
    except AssertionError as e:
        step_record["status"] = "failed"
        step_record["error"] = str(e)
        print(f"--- STEP FAILED: {description} ---")
        # Annotate assertion errors to include step context in the report
        if e.args:
            e.args = (f"[Step: {description}] {e.args[0]}",) + e.args[1:]
        else:
            e.args = (f"[Step: {description}] Assertion failed",)
        raise
    except Exception as e:
        step_record["status"] = "failed"
        step_record["error"] = str(e)
        print(f"--- STEP FAILED: {description} ---")
        # Annotate generic exceptions
        if e.args:
            args = list(e.args)
            args[0] = f"[Step: {description}] {args[0]}"
            e.args = tuple(args)
        raise

=======
import logging
from contextlib import contextmanager
import pytest

# Global list to store steps for the current test
# This is reset by the `reset_step_history` fixture in conftest.py
current_steps = []

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
>>>>>>> Add_Failed_test
