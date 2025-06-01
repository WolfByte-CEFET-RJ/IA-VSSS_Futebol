import cv2
import pickle
import sys
import os
import time
import json

from crop import select_points
from movement_diff import get_movement
from create_processed_folder import create_processed_folder

def get_points(processed_path, frame):
    points_path = os.path.join(processed_path, 'points.pkl')

    if os.path.exists(points_path):
        print (f'Carregando pontos salvos em {points_path}')
        with open(points_path, 'rb') as f:
            mask_points = pickle.load(f)
    else:
        print (f'Selecionando pontos')
        mask_points = select_points(frame)
        with open(points_path, 'wb') as f:
            pickle.dump(mask_points, f)
    
    return mask_points

def process_movement(video_path):
    cap = cv2.VideoCapture(video_path)

    # path/{file}_processed
    processed_folder = create_processed_folder(video_path)

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    with open ("options.json", "r") as f:
        skip_frames = json.load(f)["skip_frames"]

    if not cap.grab():
        return('Erro ao ler o video.')
    
    _, frame = cap.retrieve()

    print('Requisitando pontos')
    mask_points = get_points(processed_folder, frame)

    print('Criando lista de movimento')
    start_time = time.time()
    movement_list = get_movement(cap, skip_frames, mask_points)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f'Finalizado em {execution_time} segundos.')

    cap.release()

    movement_path = os.path.join(processed_folder, 'movement.pkl')
    with open(movement_path, 'wb') as f:
        pickle.dump(movement_list, f)

    cap_data = {'fps':fps, 'frame_count': frame_count}
    cap_path = os.path.join(processed_folder, 'cap_data.pkl')
    with open(cap_path, 'wb') as f:
        pickle.dump(cap_data, f)

    print(f'Movement saved in {processed_folder}')
    
    return movement_path

if __name__ == "__main__":
    video_path = sys.argv[-1]
    process_movement(video_path)