import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from .utils.captions import process_image

@csrf_exempt
def generate_caption(request):
    if request.method == 'POST':
        encoded_byte = request.body
        if encoded_byte:
            return HttpResponse(process_image(encoded_byte))
        else:
            return JsonResponse({"message": "No file uploaded"}, status=400)

    return JsonResponse({"message": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def textual_insight(request):
    if request.method == 'POST':
        body_raw = request.body
        print(body_raw)
        return HttpResponse("CSRF protection is disabled for this view.")