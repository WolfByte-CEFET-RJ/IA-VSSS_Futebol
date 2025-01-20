from ultralytics import YOLO
import cv2
import time
import numpy as np
import math


model = YOLO("vsss-pi-obb.pt")

colors = {'bola': (255, 255, 0),
          'robo': (255, 0, 0)}

def format_prediction(pred):
    cls = pred[0].obb.cls.tolist()
    conf = pred[0].obb.conf.tolist()
    xywhr = pred[0].obb.xywhr.tolist()

    formatted_list = []
    for cl, cf, cds in zip(cls, conf, xywhr):
        formatted_list.append([cl, round(cf, 2), int(cds[0]), int(cds[1]), int(cds[2]), int(cds[3]), round(cds[4], 2)])

    return formatted_list


def rotate_point(x, y, center_x, center_y, angle_degrees):
    angle_radians = math.radians(angle_degrees)
    cos_theta = math.cos(angle_radians)
    sin_theta = math.sin(angle_radians)

    # Translate the point to the origin (relative to the center)
    translated_x = x - center_x
    translated_y = y - center_y

    # Apply the rotation
    rotated_x = translated_x * cos_theta - translated_y * sin_theta
    rotated_y = translated_x * sin_theta + translated_y * cos_theta

    # Translate the point back to its original position
    final_x = rotated_x + center_x
    final_y = rotated_y + center_y

    return int(final_x), int(final_y)


cap = cv2.VideoCapture(0)
cap.set(3, 640)  
cap.set(4, 480)


latencies = []


while True:
    ret, img = cap.read()
    if not ret:
        break


    start_time = time.time()
    results = model.predict(img)
    end_time = time.time()


    latency = (end_time - start_time) * 1000
    latencies.append(latency)
    latency_text = f"Latency: {latency:.2f} ms"




    for det in format_prediction(results):

        c_x, c_y = det[2], det[3]
        x1 = det[2] - det[4]/2
        y1 = det[3] - det[5]/2
        x2 = det[2] + det[4]/2
        y2 = det[3] + det[5]/2
        rot = det[6]
        
        _cls = 'robo' if det[0] == 0 else 'bola'

        points = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]
        rect = [rotate_point(pt[0], pt[1], c_x, c_y, -rot) for pt in points]
        rect = np.array(rect, dtype=np.int32)
        rect = rect.reshape((-1, 1, 2))
        print(rect)

        img = cv2.polylines(img, pts=[rect] ,color=colors[_cls], thickness=2, isClosed=True)
        cv2.putText(img, _cls, (int(x1), int((y1 + y2)/2) - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)  

    cv2.putText(img, latency_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)  


    '''for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls = int(box.cls[0])
                print('Encontrei algo!')
                if cls == 67:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, "Celular", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)'''


    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()


average_latency = sum(latencies) / len(latencies) if latencies else 0
print(f"Latência Média: {average_latency:.2f} ms")