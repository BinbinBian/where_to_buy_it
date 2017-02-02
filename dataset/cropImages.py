
from queue import Queue
from threading import Thread
import json
import re
import os
from pprint import pprint
from PIL import Image


## Directory where all photos will be croped
BASE_CROP_DIRECTORY = 'croped'
## Directory where all photos were downloaded
BASE_IMG_DIRECTORY = 'imgs'

partitions = ['train', 'test']
categories = ['bags', 'belts', 'dresses', 'eyewear', 'footwear', 'hats', 'leggings', 'outerwear', 'pants', 'skirts', 'tops']


"""
    Crop all images bounding boxes described in json_file.

    @json_file: data set file, only test and train.
    @source_dir: directory where all images where downloaded.
    @dest_dir: directory where croped image will be saved.
"""
def cropImages (photo_id, img_name, source_dir, dest_dir): #'meta/json/test_pairs_hats.json', 'imgs/hats/test'

    #open image file from source_dir
    im = Image.open(source_dir + "/" + img_name)
    #crop image
    croppedImage = im.crop((bbox['left'],
        bbox['top'],
        bbox['left']+bbox['width'],
        bbox['top']+bbox['height']))

    #save croped image
    croppedImage.save(dest_dir + "/" + image_file_name(product, photo_id))

crop_queue = Queue()

"""
    Name of image that correspond to a product in a photo.
"""
def image_file_name(product, photo):
    return '{}@{}.jpeg'.format(photo, product)

def create_needed_directories():
    for category in categories:
        for partition in partitions:
            if not os.path.exists( directory_path(category, partition) ):
                os.makedirs( directory_path(category, partition) )

def directory_path(category, partition):
    return '{}/{}/{}'.format(BASE_CROP_DIRECTORY, category, partition)


def read_all_json_files():
    for category in categories:
        for partition in partitions:

            json_file = 'meta/json/{}_pairs_{}.json'.format(partition, category)
            dest_dir = directory_path(category, partition)

            with open(json_file) as data_file:
                data = json.load(data_file)

            for row in data:
                #Read data from json
                photo_id = row['photo']
                product = row['product']
                bbox = row['bbox']

                #name of saved image file
                img_name = '{}.jpeg'.format(int(photo_id))
                crop_queue.put((photo_id, img_name, dest_dir))

            print(dest_dir)
            print('{}\n'.format(crop_queue.qsize()))
"""
    Start croping all images. Ensure that destiny directory already exists.
"""
def start_async_crop():
    read_all_json_files()

    print('Set to crop {} images'.format(crop_queue.qsize()))

    #Each worker that consume items from photos_queue
    def worker():
        while not crop_queue.empty():
            photo_id, img_name, dest_dir = crop_queue.get()
            #proccess item
            cropImages(photo_id, img_name, BASE_IMG_DIRECTORY, dest_dir)
            crop_queue.task_done()

    # Start each worker in a diferent thread
    for i in range(NUM_WORKER_THREAD):
        t = Thread(target = worker)
        t.daemon = True
        t.start()

    crop_queue.join()
    print("All tasks completed")

if __name__ == '__main__':
    create_needed_directories()

    NUM_WORKER_THREAD = 12
    start_async_crop()
