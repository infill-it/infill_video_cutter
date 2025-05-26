import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as compare_ssim

def get_video_dimensions(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap.release()
    return height, width

def extract_frames_with_changes(
    video_path: str,
    roi: tuple[int,int,int,int],
    threshold: float,
    check_interval_s: float = 5.0
) -> list[str]:
    """
    Extrahiert alle Frames, in denen sich die ROI (region of interest) 
    mit mindestens `threshold` Score ändert.
    Dateinamen: {seconds:06d}s_frame{frame_idx:05d}.png
    Gibt Liste der gespeicherten Dateipfade zurück.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    output_files = []
    prev_roi = None
    last_ts = -1
    frame_idx = 0

    # Temp-Output-Ordner
    out_dir = os.path.join(os.path.dirname(video_path), "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray      = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi_frame = gray[roi[0]:roi[0]+roi[2], roi[1]:roi[1]+roi[3]]

        ts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        ts_s  = int(ts_ms // 1000)

        if prev_roi is None:
            prev_roi = roi_frame
            last_ts  = ts_s
            frame_idx += 1
            continue

        # nur in Intervallen prüfen
        if ts_s - last_ts >= check_interval_s:
            ssim       = compare_ssim(roi_frame, prev_roi)
            diff_score = 1 - ssim

            if diff_score >= threshold:
                # Neuer Datei-Name: 000123s_frame00042.png
                fname = f"{ts_s:06d}s_frame{frame_idx:05d}.png"
                fpath = os.path.join(out_dir, fname)
                cv2.imwrite(fpath, frame)
                output_files.append(fpath)

            prev_roi  = roi_frame
            last_ts   = ts_s

        frame_idx += 1

    cap.release()
    return output_files



def get_sample_frame(video_path: str) -> np.ndarray:
    """
    Lädt das Frame in der Mitte (halbe Anzahl Frames) und liefert es als BGR-Array zurück.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    mid_frame = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise IOError("Could not read frame at midpoint")
    return frame