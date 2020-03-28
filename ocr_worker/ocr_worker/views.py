from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.http.response import JsonResponse
from PIL import Image
import json
from ocr import OnmtOCR
from concurrent.futures import ThreadPoolExecutor
import asyncio


class OCRProcessor():
    __instance__ = None

    @staticmethod
    def get_instance():
        if OCRProcessor.__instance__ is None:
            weights_path = '/model/OnmtOCR.pt'
            OCRProcessor.__instance__ = OnmtOCR(weights_path=weights_path)
        return OCRProcessor.__instance__


def get_cropped_image(image, location):
    x1 = json.loads(format_string(location[0]))[0]
    x2 = json.loads(format_string(location[1]))[0]
    y1 = json.loads(format_string(location[0]))[1]
    y2 = json.loads(format_string(location[2]))[1]

    cropped_image = image.crop(box=(x1, y1, x2, y2))

    return cropped_image


def format_string(item):
    item = item.replace('\'', '\"')
    item = item.replace('(', '\"[')
    item = item.replace(')', ']\"')

    return item


def predict(item, image):
    if item['type'] == 'cell' and len(item['contain']) == 0:
        return {'item': item, 'result': ''}

    model = OCRProcessor.get_instance()
    location = item['location']
    ocr_image = get_cropped_image(image, location)
    result = model.process(ocr_image)
    print(result)
    return {'item': item, 'result': result}


@csrf_exempt
def process(request):
    if request.method == 'POST':
        print("POST request received")

        items = request.POST.get('items')
        items = format_string(items)
        items = json.loads(items)

        image = request.FILES['image']
        image1 = Image.open(image)

        response = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            for item in items:
                response.append(executor.submit(predict, (item), (image1)).result())

        return JsonResponse({'success': True, 'result': response})
    return HttpResponse('Welcome')
