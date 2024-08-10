import os
import numpy as np
import subprocess
from PIL import Image
import io
import shutil
from os.path import join
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from PIL import Image
import os
from runpy import run_path
from skimage import img_as_ubyte
from collections import OrderedDict
from natsort import natsorted
from glob import glob
import base64
import cv2
from ai_engine.utils.tumor_detect import *
from ai_engine.modeling.Tumor.tumor_type import *

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

def quality_improvement(task, encoded_image):
    image_bytes = base64.b64decode(encoded_image)

    # Create an in-memory stream for the image bytes
    image_stream = io.BytesIO(image_bytes)

    load_file = run_path(os.path.join("ai_engine/modeling/QualityImprovement", task, "MPRNet.py"))
    model = load_file['MPRNet']()
    model.cpu()

    weights = os.path.join("ai_engine", "pre_trained", f"model_{task.lower()}.pth")
    load_checkpoint(model, weights)
    model.eval()

    img_multiple_of = 8

    img = Image.open(image_stream).convert('RGB')
    input_ = TF.to_tensor(img).unsqueeze(0).cpu()

    # Pad the input if not_multiple_of 8
    h,w = input_.shape[2], input_.shape[3]
    H,W = ((h+img_multiple_of)//img_multiple_of)*img_multiple_of, ((w+img_multiple_of)//img_multiple_of)*img_multiple_of
    padh = H-h if h%img_multiple_of!=0 else 0
    padw = W-w if w%img_multiple_of!=0 else 0
    input_ = F.pad(input_, (0,padw,0,padh), 'reflect')

    with torch.no_grad():
        restored = model(input_)
    restored = restored[0]
    restored = torch.clamp(restored, 0, 1)

    # Unpad the output
    restored = restored[:,:,:h,:w]

    restored = restored.permute(0, 2, 3, 1).cpu().detach().numpy()
    restored = img_as_ubyte(restored[0])
    return restored

def detect_tumor(image, type):
    image_bytes = image.read()
    file_path = save_file(image_bytes, f'{type}_tumor', image.name)
    return detect(image.name, file_path, type)

def save_file(file_bytes, base_dir, filename):
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    file_path = f'{base_dir}/{filename}'
    with open(file_path, 'wb') as file:
        file.write(file_bytes)

    return file_path

def load_checkpoint(model, weights):
    checkpoint = torch.load(weights, map_location=torch.device('cpu'))

    try:
        model.load_state_dict(checkpoint["state_dict"])
    except:
        state_dict = checkpoint["state_dict"]
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:] # remove `module.`
            new_state_dict[name] = v
        model.load_state_dict(new_state_dict)