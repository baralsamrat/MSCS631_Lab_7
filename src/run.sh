#!/bin/bash
# run_program.sh
# This script sets up a Python virtual environment,
# installs required packages (if not already installed),
# and runs the video streaming program.

# Function to print usage information.
function usage(){
    echo "Usage: $0 [server|client]"
    echo "  server   --> Run only the server"
    echo "  client   --> Run only the client"
    echo "  (no arg) --> Run server in background and then client"
    exit 1
}

# Check if Python3 is installed.
if ! command -v python3 &>/dev/null; then
    echo "python3 command not found. Please install Python 3."
    exit 1
fi

# Create a virtual environment if it doesn't already exist.
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment.
source venv/bin/activate

# Upgrade pip and install required packages.
echo "Upgrading pip and installing required packages..."
pip install --upgrade pip
pip install pillow

# Check for an argument to determine which mode to run.
if [ "$#" -gt 1 ]; then
    usage
fi

# Set default RTSP parameters.
SERVER_PORT=8554        # Port for the RTSP server (>1024)
RTP_PORT=25000          # Port for the RTP stream
VIDEO_FILE="movie.Mjpeg"  # Name of the video file (should be in the current directory)
SERVER_HOST="localhost" # RTSP server host for the client

if [ "$1" == "server" ]; then
    echo "Starting the server on port ${SERVER_PORT}..."
    python Server.py ${SERVER_PORT}
elif [ "$1" == "client" ]; then
    echo "Starting the client..."
    python ClientLauncher.py ${SERVER_HOST} ${SERVER_PORT} ${RTP_PORT} ${VIDEO_FILE}
elif [ "$#" -eq 0 ]; then
    # Run both server and client.
    echo "Starting the server in the background on port ${SERVER_PORT}..."
    python Server.py ${SERVER_PORT} &
    SERVER_PID=$!
    # Give the server time to start.
    sleep 2
    echo "Starting the client..."
    python ClientLauncher.py ${SERVER_HOST} ${SERVER_PORT} ${RTP_PORT} ${VIDEO_FILE}
    # After the client ends, kill the server.
    kill ${SERVER_PID}
    echo "Server process terminated."
else
    usage
fi

# Deactivate the virtual environment at the end.
deactivate
