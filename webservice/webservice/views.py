from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .tasks import process
from django.core.files.storage import FileSystemStorage


@csrf_exempt
def upload(request):

    if request.method == 'POST' and request.FILES['image_file']:
        myfile = request.FILES['image_file']
        fs = FileSystemStorage()
        filename = request.POST['name']
        filepath = "data/%s.png" % (filename)
        path = fs.save(filepath, myfile)

        process(filename, path)

    return render(request, "upload.html", {})
