from urllib.request import urlopen

from wand.image import Image


def get_image_url_size(url):
    with Image(file=urlopen(url)) as img:
        return {"width" : img.width, "height" : img.height}


def get_image_url_width(url):
    with Image(file=urlopen(url)) as img:
        return img.width


def get_image_url_height(url):
    with Image(file=urlopen(url)) as img:
        return img.height


def get_image_size(filePath):
    with Image(filename=filePath) as img:
        return {"width" : img.width, "height" : img.height}


def get_image_width(filePath):
    with Image(filename=filePath) as img:
        return img.width


def get_image_height(filePath):
    with Image(filename=filePath) as img:
        return img.height

def get_image_url_mime_type(url):
    # TODO Check Problem BUG
    with Image(file=urlopen(url)) as img:
        return img.mimetype

def get_image_file_mime_type(file_path):
    with Image(file=file_path) as img:
        return img.mimetype

def convert_gif_to_jpg(file_path_source,file_path_dest):
    with Image(filename=file_path_source) as img:
        img.format = 'jpeg'
        img.save(filename=file_path_dest)
