import cv2
import numpy as np

from crop import crop_polygon

def gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def get_diff(img1, img2, threshold = 50):
    diff = cv2.absdiff(img1,img2)
    _, binary_mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    return binary_mask

def get_mask_volume(mask_points, shape):
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, np.array([mask_points], dtype=np.int32), 255)
    mask_volume = np.sum(mask)
    return mask_volume

def get_movement(cap, skip_frames, mask_points):
    #cap.set(cv2.CAP_PROP_POS_FRAMES, 0)#inicio
    ret, frame = cap.retrieve()
    mask_volume = get_mask_volume(mask_points, frame.shape[:2])
    frame = crop_polygon(gray(frame), mask_points)
    movement_list = []
    while True:
        last_frame = frame
        for _ in range(skip_frames):
            # Passa o frame sem decodificar
            # mais rápido que pular para o frame diretamente - deve ser causado por cache, descompressão etc
            if not cap.grab():
                break
        ret, frame = cap.read()
        if not ret:
            break

        frame = crop_polygon(gray(frame), mask_points)
        
        movement_list.append(int((np.sum(get_diff(frame, last_frame))/mask_volume)*100000))

    return movement_list