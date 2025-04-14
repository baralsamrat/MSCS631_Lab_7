# client.py
import socket
import sys
import threading
import time
from tkinter import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io

class Client:
    INIT = 0
    READY = 1
    PLAYING = 2

    SETUP    = 'SETUP'
    PLAY     = 'PLAY'
    PAUSE    = 'PAUSE'
    TEARDOWN = 'TEARDOWN'

    def __init__(self, master, server_addr, server_port, rtp_port, video_file):
        self.master = master
        self.server_addr = server_addr
        self.server_port = int(server_port)
        self.rtp_port = int(rtp_port)
        self.video_file = video_file
        self.state = self.INIT
        self.rtspSeq = 1
        self.sessionId = 0
        self.frameNbr = 0
        self.rtspSocket = None
        self.rtpSocket = None
        self.running = False  # used to control the RTP listener thread
        self.fun_mode = False  # flag for our fun overlay feature
        self.setupConnection()
        self.createWidgets()

    def setupConnection(self):
        # Establish RTSP TCP connection.
        try:
            self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rtspSocket.connect((self.server_addr, self.server_port))
            # Setup RTP UDP socket
            self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.rtpSocket.settimeout(0.5)
        except Exception as e:
            print("Error setting up connection: " + str(e))

    def createWidgets(self):
        # Create buttons and image display.
        self.setupBtn = Button(self.master, width=20, text="Setup", command=self.setupRTSP)
        self.setupBtn.grid(row=1, column=0, padx=2, pady=2)
        self.playBtn = Button(self.master, width=20, text="Play", command=self.playMovie)
        self.playBtn.grid(row=1, column=1, padx=2, pady=2)
        self.pauseBtn = Button(self.master, width=20, text="Pause", command=self.pauseMovie)
        self.pauseBtn.grid(row=1, column=2, padx=2, pady=2)
        self.teardownBtn = Button(self.master, width=20, text="Teardown", command=self.exitClient)
        self.teardownBtn.grid(row=1, column=3, padx=2, pady=2)
        # Fun Mode toggle button.
        self.funModeBtn = Button(self.master, width=20, text="Toggle Fun Mode", command=self.toggleFunMode)
        self.funModeBtn.grid(row=2, column=1, padx=2, pady=2)
        self.titleLabel = Label(self.master, text="Video Stream")
        self.titleLabel.grid(row=0, column=0, columnspan=4)
        self.imageLabel = Label(self.master)
        self.imageLabel.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

    def toggleFunMode(self):
        self.fun_mode = not self.fun_mode
        if self.fun_mode:
            print("Fun Mode Enabled!")
        else:
            print("Fun Mode Disabled!")

    def setupRTSP(self):
        if self.state == self.INIT:
            request = f"{self.SETUP} {self.video_file} RTSP/1.0\nCSeq: {self.rtspSeq}\nTransport: RTP/UDP; client_port= {self.rtp_port}\n"
            self.rtspSocket.send(request.encode())
            self.rtspSeq += 1
            response = self.rtspSocket.recv(1024).decode()
            if "200 OK" in response:
                # Parse Session ID from response.
                for line in response.split('\n'):
                    if "Session:" in line:
                        self.sessionId = int(line.split(' ')[1])
                        break
                self.state = self.READY
                print("SETUP successful, state changed to READY")
            else:
                print("SETUP failed.")

    def playMovie(self):
        if self.state == self.READY:
            request = f"{self.PLAY} {self.video_file} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}\n"
            self.rtspSocket.send(request.encode())
            self.rtspSeq += 1
            response = self.rtspSocket.recv(1024).decode()
            if "200 OK" in response:
                self.state = self.PLAYING
                print("PLAY successful, state changed to PLAYING")
                self.running = True
                self.receiveThread = threading.Thread(target=self.listenRTP)
                self.receiveThread.start()
            else:
                print("PLAY failed.")

    def pauseMovie(self):
        if self.state == self.PLAYING:
            request = f"{self.PAUSE} {self.video_file} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}\n"
            self.rtspSocket.send(request.encode())
            self.rtspSeq += 1
            response = self.rtspSocket.recv(1024).decode()
            if "200 OK" in response:
                self.state = self.READY
                self.running = False
                print("PAUSE successful, state changed to READY")
            else:
                print("PAUSE failed.")

    def exitClient(self):
        # Send TEARDOWN request and close all connections.
        request = f"{self.TEARDOWN} {self.video_file} RTSP/1.0\nCSeq: {self.rtspSeq}\nSession: {self.sessionId}\n"
        try:
            self.rtspSocket.send(request.encode())
        except:
            pass
        self.rtspSeq += 1
        self.running = False
        self.rtspSocket.close()
        self.rtpSocket.close()
        self.master.destroy()
        print("TEARDOWN: Exiting client.")

    def listenRTP(self):
        while self.running:
            try:
                data, addr = self.rtpSocket.recvfrom(20480)
                if data:
                    self.processRtpPacket(data)
            except socket.timeout:
                continue
            except Exception as e:
                print("RTP Socket error: " + str(e))
                break

    def processRtpPacket(self, packet):
        # RTP header is 12 bytes; the rest is the JPEG payload.
        header = packet[:12]
        payload = packet[12:]
        self.frameNbr += 1
        try:
            image = Image.open(io.BytesIO(payload))
            if self.fun_mode:
                image = self.applyFunOverlay(image)
            imageTk = ImageTk.PhotoImage(image)
            self.imageLabel.configure(image=imageTk)
            self.imageLabel.image = imageTk
        except Exception as e:
            print("Error decoding image: " + str(e))

    def applyFunOverlay(self, image):
        # Overlay fun text on the image.
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        text = "Fun Mode Enabled!"
        draw.text((10, 10), text, font=font, fill="red")
        return image

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python client.py <server_host> <server_port> <rtp_port> <video_file>")
        sys.exit(1)
    root = Tk()
    clientApp = Client(root, sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    root.mainloop()
