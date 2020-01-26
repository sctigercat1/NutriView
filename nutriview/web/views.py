from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from nutriview import settings

import boto3, json, urllib.request, urllib.parse
import binascii

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
    if 'labelNutrients' in response:
        labelNutrients = response['labelNutrients']
        return render(request, "nutrition.html", {"info": labelNutrients, "fdcIdOfFood": fdcIdOfFood, \
                        "food": food['description'].title(), "servingSize": round(response['servingSize']), \
                        "servingSizeUnit": response['servingSizeUnit']})

    return render(request, "error.html")

def analysis(request):
    session = boto3.Session(
        aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
        region_name="us-east-2",
    )

    # JS does not pad properly
    uri = request.POST['blob'] + '=='
    binary_uri = _parse_data_url(uri)[0]

    client = session.client('rekognition')
    response = client.detect_labels(Image={'Bytes': binary_uri})

    # Begin parsing labels -- what the AI has viewed
    labels = response['Labels']
    foods = {}
    for item in labels:
        if item['Parents'] is not None:
            for parent in item['Parents']:
                if parent['Name'] == 'Food' and item['Confidence'] > 75 and item['Name'] not in ('Fruit', 'Produce'):
                    foods[item['Name']] = item['Confidence']

    if len(foods) < 1:
        return render(request, "error.html")

    final_food = max(foods, key=foods.get) # Get key of max confidence
    
    return nutriInfo(request, final_food)

def root(request):
    return render(request, "theme_index.html")

def nutri(request):
    return render(request, "nutrition.html")


def index(request):
    return render(request, "index.html")

def error(request):
    return render(request, "error.html")

def handler404(request, *args, **argv):
    response = render(request, 'error.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response

def handler500(request, *args, **argv):
    response = render(request, 'error.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response

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
