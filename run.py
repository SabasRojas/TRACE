import subprocess
import time
import sys
import os
import signal # For sending signals

python_process = None
npm_process = None

try:
    print("Starting backend process (main.py)...")
    # Use sys.executable to ensure correct python interpreter
    python_process = subprocess.Popen(
        [sys.executable, "main.py"]
        # No stdout/stderr pipes needed - output goes to terminal
    )
    print(f"Backend PID: {python_process.pid}")

    print("Starting frontend process (npm run dev)...")
    # Using shell=True might be necessary for 'npm' on Windows if not in PATH correctly
    # but avoid if possible. If needed, set based on OS.
    is_windows = sys.platform.startswith("win")
    npm_process = subprocess.Popen(
        ["npm", "run", "dev", "--", "--host"],
        cwd="FrontEnd",
        shell=is_windows, # Often needed for npm on Windows
        # Use CREATE_NEW_PROCESS_GROUP on Win to help Ctrl+C work better
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if is_windows else 0
        # No stdout/stderr pipes needed - output goes to terminal
    )
    print(f"Frontend PID: {npm_process.pid}")

    print("\nProcesses running concurrently. Output will appear below.")
    print("Press Ctrl+C to stop both processes.")

    # Keep the main script alive and wait for processes to exit or user interrupt
    # Check periodically if either process has exited unexpectedly
    while True:
        py_exit_code = python_process.poll()
        npm_exit_code = npm_process.poll()

        if py_exit_code is not None:
            print(f"\nBackend process exited unexpectedly with code: {py_exit_code}.")
            break # Exit the loop if backend stops
        if npm_exit_code is not None:
            # npm run dev often exits if the underlying server crashes
            print(f"\nFrontend process exited unexpectedly with code: {npm_exit_code}.")
            break # Exit the loop if frontend stops
        time.sleep(1) # Wait 1 second between checks

except KeyboardInterrupt:
    print("\nCtrl+C detected. Stopping processes...")

except Exception as e:
    print(f"\nAn error occurred: {e}")
    print("Stopping processes...")

finally:
    print("Cleaning up processes...")
    processes = [proc for proc in [python_process, npm_process] if proc] # List of processes we started

    for proc in processes:
        if proc.poll() is None: # Check if the process is still running
            pid = proc.pid
            print(f"Terminating process {pid}...")
            try:
                # Send appropriate signal based on OS
                if is_windows:
                    # Send CTRL_BREAK_EVENT to the process group on Windows
                    # This is often better for terminating Node.js processes gracefully
                    os.kill(pid, signal.CTRL_BREAK_EVENT)
                else:
                    # Send SIGTERM on Unix-like systems
                    proc.terminate() # Sends SIGTERM
            except OSError as e:
                print(f"Error sending signal to process {pid}: {e}") # Process might have exited already


    # Wait a short period for processes to terminate gracefully
    print("Waiting up to 3 seconds for processes to terminate...")
    time.sleep(3)

    # Force kill any process that didn't terminate gracefully
    for proc in processes:
        if proc.poll() is None: # Check again if still running
            pid = proc.pid
            print(f"Process {pid} did not terminate gracefully, killing...")
            try:
                proc.kill() # Sends SIGKILL (force quit)
                proc.wait(timeout=1) # Wait briefly for kill to register
            except OSError as e:
                 print(f"Error killing process {pid}: {e}") # Process might have already exited
            except subprocess.TimeoutExpired:
                 print(f"WARN: Process {pid} did not exit even after kill.")


    print("Cleanup finished.")
