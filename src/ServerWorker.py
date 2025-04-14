# ServerWorker.py
import threading
import socket
import time
from VideoStream import VideoStream
from RtpPacket import RtpPacket

class ServerWorker:
    # RTSP states
    INIT = 0
    READY = 1
    PLAYING = 2

    # RTSP request types
    SETUP    = 'SETUP'
    PLAY     = 'PLAY'
    PAUSE    = 'PAUSE'
    TEARDOWN = 'TEARDOWN'

    def __init__(self, client_info):
        """
        client_info: dictionary with keys 'rtspSocket', 'client_address', and 'videoFile'
        """
        self.client_info = client_info
        self.state = self.INIT
        self.request_seq = 0
        self.session_id = 123456  # fixed session; could be randomized
        self.videoStream = None
        self.rtpSocket = None
        self.streamingThread = None

    def run(self):
        rtspSocket = self.client_info['rtspSocket']
        while True:
            try:
                data = rtspSocket.recv(256).decode()
                if data:
                    print("Received RTSP data:\n" + data)
                    self.processRtspRequest(data)
                else:
                    break
            except:
                break

    def processRtspRequest(self, data):
        """Parses RTSP request and calls the corresponding handler."""
        lines = data.split('\n')
        request_line = lines[0].split(' ')
        if len(request_line) < 2:
            return
        request_type = request_line[0]
        filename = request_line[1]
        # The sequence number is in the second line: "CSeq: <number>"
        seq_line = lines[1].split(' ')
        self.request_seq = int(seq_line[1])

        if request_type == self.SETUP:
            if self.state == self.INIT:
                # Extract client RTP port from Transport header (third line)
                transport_line = lines[2]
                client_port = int(transport_line.split('client_port=')[1])
                self.client_info['rtpPort'] = client_port
                try:
                    self.videoStream = VideoStream(self.client_info['videoFile'])
                except Exception as e:
                    print("Error opening video file: " + str(e))
                    return
                self.state = self.READY
                self.sendRtspResponse()
                self.openRtpPort()
        elif request_type == self.PLAY:
            if self.state == self.READY:
                self.state = self.PLAYING
                self.sendRtspResponse()
                self.startStreaming()
        elif request_type == self.PAUSE:
            if self.state == self.PLAYING:
                self.state = self.READY
                self.sendRtspResponse()
                self.stopStreaming()
        elif request_type == self.TEARDOWN:
            self.sendRtspResponse()
            self.stopStreaming()
            self.client_info['rtspSocket'].close()
            if self.rtpSocket:
                self.rtpSocket.close()
            print("Session Teardown: Closing RTSP and RTP sockets.")

    def sendRtspResponse(self):
        response = "RTSP/1.0 200 OK\nCSeq: " + str(self.request_seq) + \
                   "\nSession: " + str(self.session_id) + "\n"
        self.client_info['rtspSocket'].send(response.encode())

    def openRtpPort(self):
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No binding is necessary since this socket is used only for sending RTP packets.

    def startStreaming(self):
        # Start a new thread that streams the video.
        self.streamingThread = threading.Thread(target=self.streamVideo)
        self.streamingThread.start()

    def stopStreaming(self):
        self.state = self.READY

    def streamVideo(self):
        while self.state == self.PLAYING:
            data = self.videoStream.nextFrame()
            if data:
                try:
                    frame_nbr = self.videoStream.frameNbr
                    rtpPacket = RtpPacket()
                    timestamp = int(time.time() * 1000)
                    rtpPacket.encode(26, frame_nbr, data, timestamp)  # 26 for MJPEG
                    packet = rtpPacket.getPacket()
                    self.rtpSocket.sendto(packet, (self.client_info['client_address'][0],
                                                     self.client_info['rtpPort']))
                    print("Sent frame " + str(frame_nbr))
                except Exception as e:
                    print("Error sending RTP packet: " + str(e))
            else:
                print("End of video reached, stopping stream.")
                self.state = self.READY
                break
            time.sleep(0.05)  # 50 milliseconds delay between frames
