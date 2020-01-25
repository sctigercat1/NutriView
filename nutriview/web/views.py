from django.shortcuts import render
from django.http import HttpResponse
from nutriview import settings

import boto3, json

# Create your views here.
def root(request):
    session = boto3.Session(
        aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
        region_name="us-east-2",
    )
    client = session.client('rekognition')
    file = request.GET.get('img', 'pizza')
    with open(file + ".jpg", "rb") as image_file:
        response = client.detect_labels(Image={'Bytes': image_file.read()})
    
    labels = response['Labels']
    foods = []
    for item in labels:
        if item['Parents'] is not None:
            for parent in item['Parents']:
                if parent['Name'] == 'Food' and item['Confidence'] > 75:
                    foods.append(item['Name'])

    return HttpResponse(json.dumps(foods))