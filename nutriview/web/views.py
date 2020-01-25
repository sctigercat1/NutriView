from django.shortcuts import render
from django.http import HttpResponse
from nutriview import settings

import boto3, json, urllib.request, urllib.parse

def root_old(request):
    """

    """
    foods = ["Pizza"]

    # POST request to FDA site
    fda_endpoint = "https://api.nal.usda.gov/fdc/v1/search?api_key=" + settings.FDA_API_KEY

    for food in foods:
        #post_data = urllib.parse.urlencode({'generalSearchInput': food})
        data = json.dumps({'generalSearchInput': food}).encode()
        request = urllib.request.Request(fda_endpoint, data)
        request.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(request) as response:
            return HttpResponse(response.read())
            #print(f.read().decode('utf-8'))
        #response = urllib.request.urlopen(url=fda_endpoint, data=post_data)

    # return HttpResponse(json.dumps(foods))

import cv2
import time
from django.http import StreamingHttpResponse
from django.views.decorators import gzip

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret,image = self.video.read()
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def feed(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")

def snap(request):
    return render(request, "main.html")

import numpy as np
import io

def analysis(request):
    camera = cv2.VideoCapture(0)
    return_value, image=camera.read()
    cv2.imwrite('file.png',image)
    is_success, buffer = cv2.imencode(".jpg", image)
    io_buf = io.BytesIO(buffer)

    session = boto3.Session(
        aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
        region_name="us-east-2",
    )

    client = session.client('rekognition')
    response = client.detect_labels(Image={'Bytes': io_buf.read()})
    #return HttpResponse(json.dumps(response)) ###TEMP

    labels = response['Labels']
    #return HttpResponse(json.dumps(labels))
    foods = []
    for item in labels:
        if item['Parents'] is not None:
            for parent in item['Parents']:
                if parent['Name'] == 'Food' and item['Confidence'] > 75:
                    foods.append(item['Name'])
    return HttpResponse(json.dumps(foods))


    item = request.GET.get('item', 'good')
    return HttpResponse(item)

def root(request):
    return render(request, "theme_index.html")

def nutri(request):
    return render(request, "nutrition.html")
