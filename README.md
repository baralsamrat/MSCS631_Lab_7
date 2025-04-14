# Video Streaming Application using RTSP/RTP

*Happy Streaming!* 

This repository contains a Python-based video streaming application developed for a lab assignment. The application implements a simple RTSP (Real-Time Streaming Protocol) client-server model that streams a proprietary MJPEG video file. The server packetizes video frames into RTP (Real-Time Transport Protocol) packets and streams them via UDP. The client uses a GUI built with Tkinter to display the video and includes an optional “Fun Mode” that overlays a message on the video frames.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Overview

This project implements a basic video streaming system using two core protocols:
- **RTSP (Real-Time Streaming Protocol):** Used to control the streaming session (SETUP, PLAY, PAUSE, TEARDOWN).
- **RTP (Real-Time Transport Protocol):** Used to encapsulate and transmit video frames.

The streaming video is provided in a proprietary MJPEG format, where each JPEG image is preceded by a 5-byte header indicating the frame size. The application includes additional error handling in the video stream reader to gracefully handle invalid frame sizes and attempt to recover valid JPEG frames.

## Features

- **RTSP Client-Server Interaction:**  
  The client sends commands (SETUP, PLAY, PAUSE, TEARDOWN) to initiate and control the video stream.

- **RTP Packetization:**  
  The server encapsulates video frames into RTP packets with proper headers (version, payload type, sequence number, timestamp, SSRC).

- **GUI-Based Client:**  
  A Tkinter-based GUI enables users to control the stream. The client displays the video frames in real time.

- **Fun Mode:**  
  An optional mode that overlays a fun message ("Fun Mode Enabled!") on each frame.

- **Robust Video Recovery:**  
  If the video file’s frame header is invalid (e.g., an unrealistic frame size), the program attempts to recover valid JPEG frames by searching for JPEG markers.

- **Modular and Clean Code:**  
  The code is organized into separate modules for easier maintenance and extension:
  - `VideoStream.py` — Video file reading and frame extraction.
  - `RtpPacket.py` — Building and parsing RTP packets.
  - `ServerWorker.py` — Threaded worker handling RTSP sessions and streaming video frames.
  - `Server.py` — Main server that accepts client connections.
  - `client.py` — Client logic and GUI handling.
  - `ClientLauncher.py` — Launcher for the client application.
  - `movie.Mjpeg` — Sample proprietary MJPEG video file.
  - `run_program.sh` — Bash script to set up a virtual environment, install dependencies, and run the server and/or client.

## Directory Structure

```
├── ClientLauncher.py      # Launches the client GUI.
├── client.py              # Contains RTSP client and GUI implementation.
├── RtpPacket.py           # Implements RTP packet encoding.
├── Server.py              # Main RTSP server application.
├── ServerWorker.py        # Handles RTSP sessions and streams video frames.
├── VideoStream.py         # Reads and parses the proprietary MJPEG video file.
├── movie.Mjpeg            # Provided sample video file in proprietary MJPEG format.
├── run_program.sh         # Shell script for virtual environment setup and running the program.
└── README.md              # This file.
```

## Prerequisites

- **Python 3.6+**  
  Ensure you have Python 3 installed on your system.

- **Pip**  
  Used for installing required Python packages.

- **Virtualenv (optional)**  
  The provided shell script creates a virtual environment if one does not already exist.

## Installation and Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Set Up the Virtual Environment and Install Dependencies:**

   Use the provided `run_program.sh` script to automatically create a virtual environment and install the necessary packages (e.g., Pillow for image processing):

   ```bash
   chmod +x run_program.sh
   ./run_program.sh
   ```

   The script installs the required dependencies. If you prefer manual setup:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install pillow
   ```

## Running the Application

There are several ways to run the application:

### Run Both Server and Client

You can start both components using the shell script without any arguments. The script starts the server in the background, waits for it to initialize, and then launches the client GUI.

```bash
./run_program.sh
```

### Run Only the Server

To run only the server (for example, if you want to run the client separately):

```bash
./run_program.sh server
```

### Run Only the Client

Similarly, to run only the client:

```bash
./run_program.sh client
```

**RTSP/RTP Default Ports and Parameters:**

- **RTSP Server Port:** 8554  
- **RTP Port for Client:** 25000  
- **Video File:** `movie.Mjpeg`  
- **Server Host:** `localhost` (adjust if running on a different machine)

## Troubleshooting

- **Invalid Frame Header/MemoryError:**  
  If you see warnings such as:
  ```
  Warning: Detected frame size 207067558196 bytes is invalid or exceeds maximum allowed (10485760). Skipping frame.
  ```
  The `VideoStream.py` module will attempt to recover a valid JPEG frame by searching for standard JPEG markers. Ensure that the `movie.Mjpeg` file is correctly formatted.

- **Connectivity Issues:**  
  Verify that the RTSP and RTP ports are open and not blocked by your firewall or in use by another application.

- **Module Errors:**  
  Ensure that the file structure is maintained and that you are running the script from the repository's root directory so that module imports work correctly.

## Future Enhancements

- **Improved Recovery Mechanisms:**  
  Further refine the frame-recovery strategy to handle a wider variety of file corruption scenarios.

- **Dynamic Session Management:**  
  Enhance the RTSP server to handle multiple simultaneous client sessions.

- **Advanced GUI Features:**  
  Additional client features such as frame-by-frame navigation and adjustable streaming parameters.


---


