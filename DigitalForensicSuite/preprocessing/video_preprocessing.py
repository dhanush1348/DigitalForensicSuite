"""Frame extraction, face detection/alignment, resize, normalization for the
video deepfake detection pipeline. Extracts 1 frame every 0.5s by default.
"""


def extract_frames(video_path: str, fps_interval: float = 0.5):
    raise NotImplementedError


def detect_and_align_face(frame):
    raise NotImplementedError
