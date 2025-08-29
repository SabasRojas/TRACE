import subprocess
import os
import platform

def run_command(command, check=True, input=None, cwd=None, shell=False):
    """Helper function to run shell commands."""
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True, input=input, cwd=cwd, shell=shell)
        print(f"Ran: {' '.join(command)}")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error output:\n{result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        exit(1)
    except FileNotFoundError as e:
        print(f"Error: Command not found: {e.filename}. Make sure it's in your PATH.")
        exit(1)

def create_virtual_environment():
    print("\nCreating Python virtual environment...")
    if not os.path.exists("venv"):
        run_command(["python3", "-m", "venv", "venv"])
        print("Virtual environment created in 'venv' directory.")
    else:
        print("Virtual environment 'venv' already exists.")

def activate_virtual_environment():
    system = platform.system()
    activate_script = ""
    if system == "Linux" or system == "Darwin":
        activate_script = "source venv/bin/activate"
    elif system == "Windows":
        activate_script = "venv\\Scripts\\activate"

    if activate_script:
        print("\nActivating virtual environment...")
        print(f"Please run the following command in your terminal to activate the environment:")
        print(f"`{activate_script}`")
        print("You need to activate the virtual environment in your terminal session before running the installation script.")
    else:
        print(f"Warning: Could not determine activation command for {system}. Please activate the virtual environment manually.")

if __name__ == "__main__":
    create_virtual_environment()
    activate_virtual_environment()