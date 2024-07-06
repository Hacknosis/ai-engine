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

class UploadForm(forms.Form):
    report = forms.FileField(required=True)
    box = forms.CharField(required=True)
    name = forms.CharField(required=True)

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