import torch
import subprocess

yolov5_detect = 'ai_engine/modules/yolov5/detect.py'

def detect(image_name, image_path, type):
    model_path = f'ai_engine/pre_trained/{type}_tumor_detector.pt'
    command = [
        'python', yolov5_detect,
        '--weights', model_path,
        '--conf', '0.4',
        '--source', image_path,
        '--save-txt',
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Error running YOLOv5 detection: {result.stderr}")
    
    # Process the result and return the detected objects
    output_path = f'ai_engine/modules/yolov5/runs/detect/exp/{image_name}'
    with open(output_path, 'rb') as file:
        byte_array = file.read()
        return byte_array