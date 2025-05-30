import os
import cv2
import pandas as pd
import pytesseract
from pytesseract import Output

def ocr_image_to_dataframe(image_path: str) -> pd.DataFrame:
    """
    Lädt das Bild unter `image_path`, führt OCR mit pytesseract durch
    und gibt ein DataFrame zurück mit den erkannten Textblöcken und Metadaten:
    block_num, par_num, line_num, word_num, left, top, width, height, conf, text.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Bild laden (BGR) und prüfen
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise IOError(f"Failed to read image: {image_path}")

    # In RGB für pytesseract konvertieren
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # OCR durchführen
    data = pytesseract.image_to_data(img_rgb, output_type=Output.DICT)

    # Nur Einträge mit nicht-leerem Text übernehmen
    rows = []
    n_boxes = len(data["level"])
    for i in range(n_boxes):
        text = data["text"][i].strip()
        if text:
            rows.append({
                "block_num": data["block_num"][i],
                "par_num":   data["par_num"][i],
                "line_num":  data["line_num"][i],
                "word_num":  data["word_num"][i],
                "left":      data["left"][i],
                "top":       data["top"][i],
                "width":     data["width"][i],
                "height":    data["height"][i],
                "conf":      data["conf"][i],
                "text":      text
            })

    return pd.DataFrame(rows)