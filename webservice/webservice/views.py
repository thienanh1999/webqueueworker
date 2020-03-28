from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .tasks import process, get_list_of_achieved_task
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


def list_task(request):
    tasks = get_list_of_achieved_task()

    return render(request, "tasks.html", {'tasks': tasks})
