import json
import os
import io
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from PIL import Image
from .utils.process import process_image

def nparray_to_encodedbyte(image):
    image = Image.fromarray(image)

    # Create a byte buffer to store the image data
    image_buffer = io.BytesIO()
    image.save(image_buffer, format='PNG')  # Save the image in PNG format

    # Get the image data as bytes
    image_bytes = image_buffer.getvalue()

    return image_bytes

# Deblur and Denoise image
@csrf_exempt
def preprocess(request):
    if request.method == 'POST':
        encoded_byte = request.body
        if encoded_byte:
            deblurred = process_image("Deblurring", encoded_byte)

            # denoised = process_image("Denoising", encoded_byte)

            response = HttpResponse(nparray_to_encodedbyte(deblurred), content_type='image/png')

            return response
        else:
            return JsonResponse({"message": "No file uploaded"}, status=400)

    return JsonResponse({"error": "Invalid request method"})

from datetime import datetime
@csrf_exempt
def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)