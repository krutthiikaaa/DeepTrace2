import os
import cv2
import numpy as np
from backend.services.forensics import perform_ela
import tempfile

def create_temp_image(width=100, height=100, format=".jpg", color=(255, 0, 0)):
    fd, path = tempfile.mkstemp(suffix=format)
    os.close(fd)
    img = np.full((height, width, 3), color, dtype=np.uint8)
    cv2.imwrite(path, img)
    return path

def test_ela_valid_jpeg():
    path = create_temp_image(format=".jpg")
    try:
        result = perform_ela(path)
        assert result["available"] is True
        assert "ela" not in result # wait, it returns just the ela dict
        assert "mean" in result
        assert "max" in result
        assert "std" in result
        assert "anomaly_ratio" in result
        assert "image" in result
    finally:
        os.remove(path)

def test_ela_valid_png():
    path = create_temp_image(format=".png")
    try:
        result = perform_ela(path)
        assert result["available"] is True
        assert "mean" in result
    finally:
        os.remove(path)

def test_ela_corrupted_image():
    fd, path = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(b"not an image file")
    try:
        result = perform_ela(path)
        assert result["available"] is False
        assert "error" in result
    finally:
        os.remove(path)

def test_ela_empty_image():
    fd, path = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    try:
        result = perform_ela(path)
        assert result["available"] is False
        assert "error" in result
    finally:
        os.remove(path)

def test_ela_very_small_image():
    path = create_temp_image(width=10, height=10, format=".jpg")
    try:
        result = perform_ela(path)
        assert result["available"] is False
        assert "error" in result
    finally:
        os.remove(path)
