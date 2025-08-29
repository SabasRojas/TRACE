import subprocess
import shutil
import platform # Import platform
import os
import sys # Import sys

FRONTEND_DIR = "FrontEnd"

# Improved run_command with better logging and error handling
def run_command(command, check=True, input=None, cwd=None, shell=False):
    """Helper function to run shell commands."""
    # Log the command being run clearly
    cmd_str = command if isinstance(command, str) else ' '.join(command)
    location = f" in '{cwd}'" if cwd else ""
    shell_info = " with shell=True" if shell else ""
    print(f"Running: {cmd_str}{location}{shell_info}")
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True, input=input, cwd=cwd, shell=shell)
        # Print stdout/stderr only if they contain something
        if result.stdout:
            print(f"Output:\n{result.stdout.strip()}")
        if result.stderr:
            print(f"Stderr output:\n{result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed: {cmd_str}")
        print(f"Return code: {e.returncode}")
        if e.stdout: print(f"Stdout:\n{e.stdout.strip()}")
        if e.stderr: print(f"Stderr:\n{e.stderr.strip()}")
        exit(1) # Exit on error
    except FileNotFoundError as e:
        print(f"ERROR: Command or executable not found: '{e.filename}'.")
        print("Please ensure it is installed and correctly added to your system's PATH.")
        if "npm" in e.filename:
             print("Specifically for 'npm', ensure Node.js is installed and includes npm in PATH.")
        exit(1) # Exit on error
    except Exception as e_general: # Catch other potential errors
         print(f"ERROR: An unexpected error occurred running {cmd_str}: {e_general}")
         exit(1)

# Slightly improved check and guidance
def install_npm():
    print("\nChecking for Node.js and npm...")
    # Check both node and npm are findable
    node_path = shutil.which("node")
    npm_path = shutil.which("npm")

    if node_path and npm_path:
        print(f"Node found: {node_path}")
        print(f"npm found: {npm_path}")
        # Optionally check versions here if needed:
        # run_command(["node", "--version"])
        # run_command(["npm", "--version"])
        return True # Indicate found

    system = platform.system()
    print("\n*** ACTION REQUIRED ***")
    if system == "Windows":
        print("Node.js and/or npm NOT found in your system PATH.")
        print("Please download and install Node.js (which includes npm)")
        print("from the official website: https://nodejs.org/")
        print("IMPORTANT: During installation, ensure the option 'Add to PATH' is SELECTED.")
    elif system == "Linux" or system == "Darwin":
        print(f"Node.js and/or npm NOT found for {system}.")
        print("Please install Node.js and npm using your system's package manager (e.g., apt, brew)")
        print("or download from https://nodejs.org/.")
    else:
        print(f"Unsupported OS: {system}. Please install Node.js and npm manually.")

    print("\nAfter installation, please RESTART your terminal or command prompt")
    print("and re-run this script.")
    exit(1) # Exit script if not found


def install_node_dependencies():
    print("\nInstalling Node dependencies...")
    if os.path.isdir(FRONTEND_DIR):
        print(f"Running 'npm install' in directory: {FRONTEND_DIR}")

        # --- FIX: Set shell=True specifically for Windows ---
        is_windows = platform.system() == "Windows"
        run_command(["npm", "install"], cwd=FRONTEND_DIR, shell=is_windows)
        # --- END FIX ---

        print("Node dependencies installation command finished.")
    else:
        print(f"Warning: Directory '{FRONTEND_DIR}' not found. Skipping Node dependency installation.")

# Improved Python dependency installation (uses current python env)
def install_python_dependencies():
    print("\nInstalling Python dependencies...")
    if os.path.exists("requirements.txt"):
         # Use sys.executable to get path to current python interpreter
         # Then derive the pip path within that environment
         python_executable = sys.executable
         pip_executable = os.path.join(os.path.dirname(python_executable), "pip")
         # Add .exe for windows
         if platform.system() == "Windows":
             pip_executable += ".exe"

         print(f"Using pip from current Python environment: {pip_executable}")
         if os.path.exists(pip_executable):
            run_command([pip_executable, "install", "-r", "requirements.txt"])
            print("Python dependencies installation command finished.")
         else:
             print(f"ERROR: Could not find pip at '{pip_executable}'.")
             print("Please ensure pip is installed in your Python environment.")
             print("If using a virtual environment, make sure it's activated before running this script.")
             # Consider exiting or allowing script to continue
             # exit(1)
    else:
        print("Warning: requirements.txt not found. Skipping Python dependency installation.")

def install_neo4j():
    print("\nSetting up Neo4j...")
    print("Automatic Neo4j installation is not fully reliable on Kali Linux due to potential systemd and dependency issues.")
    print("Please follow these steps to install Neo4j manually:")
    print("1.  Download the Neo4j Debian package from the official website: https://neo4j.com/download-center/#releases")
    print("2.  Install the package using dpkg:")
    print("    `sudo dpkg -i <neo4j_package_name>.deb`")
    print("3.  Fix any dependency issues (if any):")
    print("    `sudo apt-get -f install`")
    print("4.  Start the Neo4j service:")
    print("    `sudo systemctl start neo4j`")
    print("5.  Enable the Neo4j service to start on boot:")
    print("    `sudo systemctl enable neo4j`")

def main():
    print("Starting TRACE dependencies installation...")
    install_npm()
    install_node_dependencies()
    install_python_dependencies()
    install_neo4j()
    print("\nTRACE dependencies installation complete!")
if __name__ == "__main__":
    main()