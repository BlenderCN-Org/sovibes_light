import json
import traceback
import urllib
from urllib import request

import youtube_dl
from youtube_dl import DEFAULT_OUTTMPL
import os


def download_youtube_video(youtube_id, directory_path):
    destination_file_path = ''
    youtubeDownloader = youtube_dl.YoutubeDL({'nocheckcertificate': True,'outtmpl' : directory_path + '/' + '%(display_id)s'})
    try:
        result = youtubeDownloader.extract_info(youtube_id, download=True)
        # print(json.dumps(result,indent=2,sort_keys=True))
        destination_file_path = directory_path + '/' + result['display_id'] + '.mkv'
        if os.path.exists(directory_path + '/'+ result['display_id'] + '.mkv'):
            destination_file_path = directory_path + '/' + result['display_id'] + '.mkv'
        elif os.path.exists(directory_path + '/' + result['display_id'] + '.mp4'):
            destination_file_path = directory_path + '/' + result['display_id'] + '.mp4'
        elif os.path.exists(directory_path + '/' + result['display_id'] + '.webm'):
            destination_file_path = directory_path + '/' + result['display_id'] + '.webm'
        elif os.path.exists(directory_path + '/' + result['display_id']):
            destination_file_path = directory_path + '/' + result['display_id']

        print(destination_file_path)
        return destination_file_path
    except:
        print('Impossible to Download youtube video id : ' + youtube_id)


def get_video_info_url(url):
    youtube_downloader = youtube_dl.YoutubeDL()
    info = youtube_downloader.extract_info(url, download=False)

    return json.dumps(info, indent=2, sort_keys=True)


def url_file_exists(url):
    try:
        return_status = urllib.request.urlopen(url).status
        if return_status == 200:
            return True
    except ValueError:
        traceback.print_exc()
    return False


def download_url_to_file(url, filePath):

    return request.urlretrieve(request.unquote(url),filePath)

def download_youtube_video_by_id(id,destFilePath):
    pass

def download_youtube_video_by_url(url,destFilePath):
    pass