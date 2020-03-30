from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .tasks import process, get_list_of_achieved_task, get_task_by_id
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
    for task in tasks:
        task['id'] = task['_id']

    return render(request, "tasks.html", {'tasks': tasks})


def task_detail(request, task_id):
    # task_id = '5e81758027e1da705b876436'
    task = get_task_by_id(task_id)
    task['file_path'] = '../' + task['file_path']
    for i in range(len(task['result'])):
        task['result'][i]['item']['path'] = '../' + task['result'][i]['item']['path']

    return render(request, "task_detail.html", {'image': task['file_path'], 'result': task['result']})
