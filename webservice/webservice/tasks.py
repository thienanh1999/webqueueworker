from __future__ import absolute_import, unicode_literals
import logging
import requests
import pymongo
from layout.tadashi.model import TadashiLayout
import cv2
import io
from bson.objectid import ObjectId
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .celery import app

logger = logging.getLogger("celery")


class DatabaseManager():
    __instance__ = None
    connection = None
    database = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if DatabaseManager.__instance__ is None:
            DatabaseManager.__instance__ = DatabaseManager()
        return DatabaseManager.__instance__

    def __init__(self):
        """ Virtually private constructor """
        if DatabaseManager.__instance__ is None:
            database_manager = self
            database_manager.connection = pymongo.MongoClient('mongodb://172.22.0.2:27017')
            database_manager.database = database_manager.connection["database"]
            DatabaseManager.__instance__ = database_manager
        else:
            raise Exception("This Class is a Singleton")

    def save_data(self, record):
        collection = self.database["task"]
        x = collection.insert_one(record)
        logger.info("-" * 25)
        logger.info("Inserted new record: ")
        print(x.inserted_id)

    def get_all_data(self):
        collection = self.database["task"]
        data = []

        for x in collection.find():
            data.append(x)

        return data

    def drop_collection(self, collection_name):
        collection = self.database[collection_name]
        collection.drop()

    def get_task_by_id(self, task_id):
        collection = self.database["task"]
        query = {"_id": ObjectId(task_id)}
        x = collection.find_one(query)

        return x


class LayoutProcessor():
    __instance__ = None

    @staticmethod
    def get_instance():
        if LayoutProcessor.__instance__ is None:
            weights_path = {
                "textline": "/model/Tadashi/frozen_model_textline.pb",
                "border": "/model/Tadashi/frozen_model_border.pb"
            }
            LayoutProcessor.__instance__ = TadashiLayout(weights_path=weights_path)
        return LayoutProcessor.__instance__


def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def get_cropped_image(image, location):
    x1 = location[0][0]
    x2 = location[1][0]
    y1 = location[0][1]
    y2 = location[2][1]

    cropped_image = image[y1:y2, x1:x2]

    return cropped_image


def post_request(ocr_worker, data):
    files = {
        'image': data['image']
    }
    response = requests.post(ocr_worker, files=files)
    result = response.json()['result']
    result = {
        'path': data['path'],
        'result': result
    }

    return result


async def send_async_request(image_list, result):
    with ThreadPoolExecutor(max_workers=12) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                post_request,
                *('http://172.22.0.5:8001/single', data)
            )
            for data in image_list
        ]
        result.extend(await asyncio.gather(*tasks))


def send_request_to_ocr_worker(image_list):
    result = list()

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(send_async_request(image_list, result))
    loop.run_until_complete(future)

    return result


@app.task
# Auto layout process
def process(task_name, filepath):
    logger.info("-"*25)
    logger.info("Celery received new task!")
    logger.info(task_name)
    logger.info(filepath)

    # Process layout
    layout_model = LayoutProcessor.get_instance()
    result = layout_model.process(cv2.imread(filepath))

    # Get image in byte
    with open(filepath, 'rb') as image:
        file = image.read()
        image_in_byte = io.BytesIO(file)

    # Save all cropped images
    my_image = cv2.imread(filepath)
    image_list = []
    folder = filepath.split('.')[0]
    for id in range(len(result)):
        item = result[id]
        cropped_image = get_cropped_image(my_image, item['location'])
        path = folder + "_image-{:03d}.png".format(id+1)
        result[id]['path'] = path
        cv2.imwrite(path, cropped_image)

        image = open(path, 'rb')
        file = image.read()
        image_in_byte = io.BytesIO(file)
        image_list.append(
            {
                'image': image_in_byte,
                'path': path,
            }
        )

    image_list = chunkIt(image_list, 3)

    data = send_request_to_ocr_worker(image_list[0])
    data = data.append(send_request_to_ocr_worker(image_list[1]))

    # Save task to database
    my_job = {
        'job_name': task_name,
        'file_path': filepath,
        'result': data,
    }
    database_manager = DatabaseManager.get_instance()
    # database_manager.drop_collection("task")
    database_manager.save_data(my_job)
    # print(database_manager.get_all_data())


def get_list_of_achieved_task():
    database_manager = DatabaseManager.get_instance()
    return database_manager.get_all_data()


def get_task_by_id(task_id):
    database_manager = DatabaseManager.get_instance()
    return database_manager.get_task_by_id(task_id)
