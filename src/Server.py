# Server.py
import sys
import socket
import threading
from ServerWorker import ServerWorker

def main():
    if len(sys.argv) != 2:
        print("Usage: python Server.py <server_port>")
        sys.exit(1)

    server_port = int(sys.argv[1])
    rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rtspSocket.bind(('', server_port))
    rtspSocket.listen(5)
    print("Server started on port " + str(server_port))

    while True:
        client_info = {}
        client_info['rtspSocket'], client_info['client_address'] = rtspSocket.accept()
        print("Accepted RTSP connection from " + str(client_info['client_address']))
        # In this assignment we assume the video file is fixed.
        client_info['videoFile'] = "movie.Mjpeg"
        worker = ServerWorker(client_info)
        threading.Thread(target=worker.run).start()

if __name__ == "__main__":
    main()
