import cv2
import numpy as np

def crop_polygon(image, points):
    if len(points) < 3:
        return np.zeros_like(image)
    
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    pts = np.array([points], dtype=np.int32)
    cv2.fillPoly(mask, pts, 255)
    masked = cv2.bitwise_and(image, image, mask=mask)
    x, y, w, h = cv2.boundingRect(pts)
    return masked[y:y+h, x:x+w] if w > 0 and h > 0 else masked

def select_points(image):
    print("""Selecione os pontos.
          Botão direito para adicionar
          Botão esquerdo para remover o último
          ESC para finalizar""")
    WINDOW_NAME =  "Select Points"
    image = image.copy()
    image_display = image.copy()
    points = []

    def click_event(event, x, y, flags, param):
        nonlocal points, image_display

        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            image_display = image.copy()
            for pt in points:
                cv2.circle(image_display, pt, 5, (0, 255, 0), -1)
            update_preview()
        elif event == cv2.EVENT_RBUTTONDOWN:
            if points:
                points.pop()
                image_display = image.copy()
                for pt in points:
                    cv2.circle(image_display, pt, 5, (0, 255, 0), -1)
                update_preview()

    def update_preview():
        if len(points) >= 3:
            preview = crop_polygon(image, points)
        else:
            preview = np.ones((100, 100, 3), dtype=np.uint8) * 50
        cv2.imshow("Preview", preview)
        cv2.imshow(WINDOW_NAME, image_display)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW_NAME, click_event)

    update_preview()

    while True:
        cv2.imshow(WINDOW_NAME, image_display)
        key = cv2.waitKey() & 0xFF
        if key == 27:  # ESC to finish
            break

    cv2.destroyAllWindows()

    return points