from django.shortcuts import render
from django.http import HttpResponse
from nutriview import settings

import boto3, json, urllib.request, urllib.parse
import binascii

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

def snap(request):
    return render(request, "snap.html")

def nutriInfo(request, food):
    # Get FDCID for food
    fda_endpoint = "https://api.nal.usda.gov/fdc/v1/search?api_key=" + settings.FDA_API_KEY
    data = json.dumps({'generalSearchInput': food}).encode()
    r = urllib.request.Request(fda_endpoint, data)
    r.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(r) as response:
        response = json.loads(response.read())

    # Read initial response data
    foods = response['foods']
    #return HttpResponse(json.dumps(foods))
    food = foods[0] # First choice food
    fdcIdOfFood = food['fdcId']
    # Request nutritional info about this one food
    endpoint = "https://api.nal.usda.gov/fdc/v1/%i?api_key=%s" % (fdcIdOfFood, settings.FDA_API_KEY)
    with urllib.request.urlopen(endpoint) as data:
        response = json.loads(data.read())
    #return HttpResponse(json.dumps(response))

    # Parse data
    labelNutrients = response['labelNutrients']
    return render(request, "nutrition.html", {"info": labelNutrients, "fdcIdOfFood": fdcIdOfFood})

def analysis(request):
    session = boto3.Session(
        aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
        region_name="us-east-2",
    )

    uri = request.POST['blob'] + '=='
    binary_uri = _parse_data_url(uri)[0]

    client = session.client('rekognition')
    response = client.detect_labels(Image={'Bytes': binary_uri})
    #return HttpResponse(json.dumps(response)) ###TEMP

    labels = response['Labels']
    foods = []
    for item in labels:
        if item['Parents'] is not None:
            for parent in item['Parents']:
                if parent['Name'] == 'Food' and item['Confidence'] > 75 and item['Name'] not in ('Fruit'):
                    foods.append({item['Name']: item['Confidence']})

    if len(foods) < 1:
        pass

    final_food = max(foods, key=foods.get) # Get max confidence
    
    return nutriInfo(request, final_food)

def root(request):
    return render(request, "theme_index.html")

def nutri(request):
    return render(request, "nutrition.html")


def index(request):
    return render(request, "index.html")

def error(request):
    return render(request, "error.html")

def _parse_data_url(url):
	scheme, data = url.split(":",1)
	assert scheme == "data", "unsupported scheme: "+scheme
	mediatype, data = data.split(",",1)
	# base64 urls might have a padding which might (should) be quoted:
	data = urllib.parse.unquote_to_bytes(data)
	if mediatype.endswith(";base64"):
		return binascii.a2b_base64(data), mediatype[:-7] or None
	else:
		return data, mediatype or None
