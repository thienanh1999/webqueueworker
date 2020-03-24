import json
import io
from PIL import Image
import numpy as np
import cv2


raw = "{\"location\": [\"(68, 34)\", \"(312, 34)\"], \"type\": \"textline\"}"
print(raw)
fin = json.loads(raw)
print(fin['location'][0])

with open('sample.jpg', 'rb') as image:
    f = image.read()
    # print(f)
    b = io.BytesIO(f)
    # print(b)

    img = Image.open(b)
    # print(img)
    np_img = np.asarray(img, dtype=np.float32)
    # print(np_img)

c_image = img.crop(box=(68, 34, 312, 70))
c_image.show()


def get_cropped_image(image, location):
    x1 = location[0][0]
    x2 = location[1][0]
    y1 = location[0][1]
    y2 = location[2][1]

    print(str(x1) + " " + str(x2) + " " + str(y1) + " " + str(y2))

    cropped_image = image[y1:y2, x1:x2]

    return cropped_image


image1 = cv2.imread('sample.jpg')
image2 = np_img

crop_image = get_cropped_image(cv2.imread('sample.jpg'), [(316, 1354), (1562, 1354), (1562, 1474), (316, 1474)])

cv2.imshow('image', crop_image)
cv2.waitKey(0)
