import open_clip
import torch
from PIL import Image
import base64
import io

def process_image(encoded_image):
    """
    Helper function to process the image and returns caption associated with it
    """
    print('encoded binary string is: ', encoded_image)
    model, _, transform = open_clip.create_model_and_transforms(
        model_name="coca_ViT-L-14",
        pretrained="mscoco_finetuned_laion2B-s13B-b90k"
    )

    # Convert the base64 encoded string to bytes
    image_bytes = base64.b64decode(encoded_image)

    # Create an in-memory stream for the image bytes
    image_stream = io.BytesIO(image_bytes)
    
    im = Image.open(image_stream).convert("RGB")
    im = transform(im).unsqueeze(0)

    with torch.no_grad(), torch.cuda.amp.autocast():
        generated = model.generate(im, num_beam_groups=1)

    return open_clip.decode(generated[0]).split("<end_of_text>")[0].replace("<start_of_text>", "")