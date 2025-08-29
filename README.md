# TRACE System – Fullstack Reconnaissance Platform

TRACE (Targeted Reconnaissance for Advanced Content Exploitation) is a full-stack platform for automated web application scanning, crawling, and testing. It integrates Python-based backend modules with a SvelteKit frontend dashboard for seamless reconnaissance.

## Project Structure
CS4311_TRACE_Beta_Spring2025/
- backend/                # Python backend modules (crawler, fuzzer, etc.)
- src/                    # SvelteKit frontend code
- venv/                   # Python virtual environment
- create_env.py           # Creates virtual environment
- setup.py                # Installs Python dependencies
- run.py                  # Starts backend server
- requirements.txt        # Python dependencies
- package.json            # Node.js dependencies for frontend
- README.md               # Project documentation

## Prerequisites

- Kali Linux VM 
- Python 3.8+
- Node.js 16+ (via NodeSource)
- npm 8+
- Neo4j (for data storage)
- Git

## Installation

Follow these steps to set up TRACE on a Kali Linux virtual machine, assuming the repository is already cloned:
   
1. **Set Up Python Environment**
    Create and activate a virtual environment, then install dependencies:
    python3 create_env.py
    source venv/bin/activate
    python3 setup.py
    Note: Expected dependencies include requests, beautifulsoup4, nltk, and neo4j. Update requirements.txt if needed.
2. **Install Neo4j**
    Configure the Neo4j repository and install:
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
    echo 'deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
    sudo apt update
    sudo apt install -y neo4j
    sudo neo4j start
    Verify Neo4j is running:
    sudo neo4j status
   (May need to update password in neo4j browser: localhost:7474)
4. **Launch the Application**
     python3 run.py

## Usage
### Running TRACE locally in the same machine:
1. Open `http://localhost:5173` in a browser.

### Connecting to another machine:
#### On the machine running the backend:
1. Open `http://localhost:5173` in a browser.
2. Open settings.
3. Take note of the IP address shown.
#### On the machine connecting to the backend:
1. Run the frontend using npm run dev
2. Open `http://localhost:5173` in a browser.
3. Open settings.
4. Enter the IP address of the machine you wish to connect to and click save.
## Troubleshooting

- **Neo4j Not Starting**:
  - Verify installation: `sudo neo4j status`.
  - Check logs: `cat /var/log/neo4j/neo4j.log`.
  - Ensure port 7474 is free: `netstat -tuln | grep 7474`.
- **Python Errors**:
  - Ensure `venv` is activated: `source venv/bin/activate`.
  - Install missing packages: `pip install <package>`.
  - Ensure you are using python3.
- **Frontend Not Loading**:
  - Check `http://localhost:5173` in a browser.
  - Confirm connection with backend.
- **Node.js Issues**:
  - Verify `node -v` returns v16+. Reinstall if needed.
  - Delete package.json and package-lock.json and run setup.py again.
