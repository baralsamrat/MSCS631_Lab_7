# VideoStream.py
import os

class VideoStream:
    """
    Class that reads video frames from a proprietary MJPEG file.
    Each frame is prefixed by a 5-byte header that indicates the frame size.
    """
    # Maximum allowed frame size (10 MB in this example)
    MAX_FRAME_SIZE = 10 * 1024 * 1024

    def __init__(self, filename):
        self.filename = filename
        try:
            self.file = open(filename, 'rb')
        except Exception as e:
            raise Exception("Unable to open video file: " + filename + ". Error: " + str(e))
        self.frameNbr = 0

    def nextFrame(self):
        try:
            # Read the 5-byte header for the frame size.
            header = self.file.read(5)
            if len(header) < 5:
                return None  # End of file reached.
            frameSize = int.from_bytes(header, byteorder='big')

            # Sanity check on the frame size.
            if frameSize <= 0 or frameSize > VideoStream.MAX_FRAME_SIZE:
                print(f"Warning: Detected frame size {frameSize} bytes is invalid or exceeds maximum allowed ({VideoStream.MAX_FRAME_SIZE}). Skipping frame.")
                # Try to skip this frame if possible.
                self.file.seek(frameSize, os.SEEK_CUR)
                return None

            # Read the frame data based on the frame size.
            data = self.file.read(frameSize)
            if len(data) < frameSize:
                return None  # Incomplete frame or error.
            self.frameNbr += 1
            return data

        except MemoryError:
            # Handle case when read request is too large.
            print("MemoryError encountered: frame size may be corrupted. Skipping this frame.")
            return None
        except Exception as e:
            print("Error reading frame: " + str(e))
            return None

    def reset(self):
        # Optionally allow restarting the video stream.
        self.file.seek(0)
        self.frameNbr = 0
