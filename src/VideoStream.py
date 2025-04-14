# VideoStream.py
import os

class VideoStream:
    """
    Class that reads video frames from a proprietary MJPEG file.
    Each frame is prefixed by a 5-byte header that indicates the frame size.
    If the header appears invalid, a recovery mechanism searches for valid JPEG markers.
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
            # Remember the current position in the file (for recovery if needed).
            start_position = self.file.tell()

            # Read the 5-byte header for the frame size.
            header = self.file.read(5)
            if len(header) < 5:
                # End of file reached.
                return None

            frameSize = int.from_bytes(header, byteorder='big')

            # Get the remaining bytes in the file.
            file_size = os.fstat(self.file.fileno()).st_size
            remaining_bytes = file_size - self.file.tell()

            # Check if the frameSize seems outlandish.
            if frameSize <= 0 or frameSize > remaining_bytes or frameSize > VideoStream.MAX_FRAME_SIZE:
                print(f"Warning: Detected frame size {frameSize} bytes is invalid or exceeds maximum allowed ({VideoStream.MAX_FRAME_SIZE}). Attempting recovery...")

                # Reset file pointer to before the header.
                self.file.seek(start_position)
                # Read a larger block of data to search for JPEG markers.
                # Adjust the chunk size as needed.
                chunk_size = 50 * 1024  # 50KB chunk
                data_chunk = self.file.read(chunk_size)

                # Find JPEG start and end markers.
                start_marker = data_chunk.find(b'\xff\xd8')
                # Look for the JPEG end marker after the start marker.
                end_marker = data_chunk.find(b'\xff\xd9', start_marker + 2) if start_marker != -1 else -1

                if start_marker != -1 and end_marker != -1:
                    # Recovered frame data between the markers.
                    frame_data = data_chunk[start_marker:end_marker + 2]
                    self.frameNbr += 1

                    # Move the file pointer to after the recovered frame.
                    new_position = start_position + start_marker + len(frame_data)
                    self.file.seek(new_position)
                    print(f"Recovered frame {self.frameNbr} from position {start_position} to {new_position}.")
                    return frame_data
                else:
                    print("Recovery failed: valid JPEG markers not found.")
                    # Skip the chunk to avoid an infinite loop.
                    self.file.seek(start_position + len(data_chunk))
                    return None

            # Otherwise, if frameSize looks valid, read the frame data.
            data = self.file.read(frameSize)
            if len(data) < frameSize:
                return None  # Incomplete frame.
            self.frameNbr += 1
            return data

        except MemoryError:
            print("MemoryError encountered: frame size may be corrupted. Skipping this frame.")
            return None
        except Exception as e:
            print("Error reading frame: " + str(e))
            return None

    def reset(self):
        # Allow restarting the video stream.
        self.file.seek(0)
        self.frameNbr = 0
