#!/user/bin/env python
# -*- coding: utf-8 -*-
import sys
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif(file,field):

    img = Image.open(file)
    exif = img._getexif()


    exif_data = []
    for id, value in exif.items():
        if TAGS.get(id) == field:
            tag = TAGS.get(id, id),value
            exif_data.extend(tag)


    return exif_data

my_img = "/home/pi/Pictures/photo_1564121933757.jpeg"
print(get_exif(my_img,"DateTimeOriginal"))
