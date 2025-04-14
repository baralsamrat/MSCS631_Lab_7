# RtpPacket.py
import time

class RtpPacket:
    HEADER_SIZE = 12  # RTP header size is 12 bytes

    def __init__(self):
        self.header = bytearray(self.HEADER_SIZE)
        self.payload = bytes()

    def encode(self, payload_type, frame_nbr, payload, timestamp=None, ssrc=0x12345678):
        """
        Encapsulate the payload into an RTP packet.
        
        Arguments:
          payload_type -- type of payload (for MJPEG, use 26)
          frame_nbr    -- frame sequence number (used as RTP sequence number)
          payload      -- binary image data (JPEG encoded)
          timestamp    -- timestamp for the RTP packet (if None, current time is used)
          ssrc         -- source identifier (default is fixed, but could be randomized)
        """
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        # First byte: Version (2 bits), Padding (0), Extension (0), CC (0)
        self.header[0] = 0x80  # 10000000 in binary: Version=2, P=0, X=0, CC=0

        # Second byte: Marker (0) and Payload Type (7 bits). For MJPEG, payload type is 26.
        self.header[1] = payload_type & 0x7F

        # Sequence number: 16 bits.
        self.header[2] = (frame_nbr >> 8) & 0xFF
        self.header[3] = frame_nbr & 0xFF

        # Timestamp: 32 bits.
        self.header[4] = (timestamp >> 24) & 0xFF
        self.header[5] = (timestamp >> 16) & 0xFF
        self.header[6] = (timestamp >> 8) & 0xFF
        self.header[7] = timestamp & 0xFF

        # SSRC: 32 bits.
        self.header[8]  = (ssrc >> 24) & 0xFF
        self.header[9]  = (ssrc >> 16) & 0xFF
        self.header[10] = (ssrc >> 8) & 0xFF
        self.header[11] = ssrc & 0xFF

        self.payload = payload

    def getPacket(self):
        return self.header + self.payload

    def getHeader(self):
        return self.header

    def getPayload(self):
        return self.payload
