import random

import cv2

def get_file_range(file_path, start, end):
    with open(file_path, 'rb') as f:
        f.seek(start)
        return f.read(end - start)

def create_thumbnail(video_path, thumb_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    capture_frame = (total_frames * random.randint(1, 15)) // 100

    cap.set(cv2.CAP_PROP_POS_FRAMES, capture_frame)

    ret, frame = cap.read()
    cv2.imwrite(thumb_path, cv2.resize(frame, (800, 450)))

    cap.release()