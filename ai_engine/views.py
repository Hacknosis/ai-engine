import base64
import json
import os
import io
import ast
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django import forms
from PIL import Image
from datetime import datetime
from .utils.process import segment
from .utils.process import quality_improvement

class UploadForm(forms.Form):
    report = forms.FileField(required=True)
    box = forms.CharField(required=True)
    name = forms.CharField(required=True)

def nparray_to_encodedbyte(image):
    image = Image.fromarray(image)

    # Create a byte buffer to store the image data
    image_buffer = io.BytesIO()
    image.save(image_buffer, format='PNG')  # Save the image in PNG format

    # Get the image data as bytes
    image_bytes = image_buffer.getvalue()

    return image_bytes

# Segment image
@csrf_exempt
def segment_image(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['report']
            file_bytes = file.read()
            box = ast.literal_eval(form.cleaned_data['box'])
            name = form.cleaned_data['name']

            raw_bytes = segment(file_bytes, box, name)
            image_base64 = base64.b64encode(raw_bytes).decode('utf-8')

            return JsonResponse({"encodedBytes": image_base64}, status = 200)
        else:
            print("Form errors:", form.errors)
            return JsonResponse({"message": "Invalid request data"}, status=400)
    return JsonResponse({"error": "Invalid request method"})

# Pre-process image
@csrf_exempt
def preprocess_image(request):
    if request.method == 'POST':
        encoded_byte = request.body
        if encoded_byte:
            deblurred = quality_improvement("Deblurring", encoded_byte)

            # denoised = quality_improvement("Denoising", encoded_byte)

            response = HttpResponse(nparray_to_encodedbyte(deblurred), content_type='image/png')

            return response
        else:
            return JsonResponse({"message": "No file uploaded"}, status=400)

    return JsonResponse({"error": "Invalid request method"})

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