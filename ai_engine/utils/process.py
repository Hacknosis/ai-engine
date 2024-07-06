import os
import numpy as np
import subprocess
from PIL import Image
import io
import shutil
from os.path import join

pre_trained_model = 'ai_engine/pre_trained/lite_medsam.pth'
medsam = 'ai_engine/utils/CVPR24_LiteMedSAM_infer.py'

def segment(file_bytes, box, file_name):
    input_file_dir = f"./input/{file_name.split('.')[0]}"
    output_file_path = f"./output/{file_name.split('.')[0]}"
    overlay_path = "./overlay"
    if not os.path.exists(input_file_dir):
        os.makedirs(input_file_dir)
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    image = Image.open(io.BytesIO(file_bytes))
    image = image.convert('RGB')

    image = image.resize((256, 256), Image.ANTIALIAS)

    npz_file_path = os.path.join(input_file_dir, f"{file_name.split('.')[0]}.npz")
    np.savez(npz_file_path, imgs=image, boxes=np.array([box]))

    command = [
        'python', medsam,
        '--input_dir', input_file_dir,
        '--output_dir', output_file_path,
        '-lite_medsam_checkpoint_path', pre_trained_model
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print("Output: ", result.stdout)
    print("Errors: ", result.stderr)
    with open(f'{output_file_path}/{file_name}', 'rb') as file:
        byte_array = file.read()

    os.remove(npz_file_path)
    shutil.rmtree(input_file_dir)
    shutil.rmtree(output_file_path)
    
    return byte_array
