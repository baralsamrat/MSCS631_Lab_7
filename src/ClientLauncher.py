# ClientLauncher.py
import sys
from tkinter import Tk
from client import Client

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python ClientLauncher.py <server_host> <server_port> <rtp_port> <video_file>")
        sys.exit(1)
    root = Tk()
    clientApp = Client(root, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    root.mainloop()
