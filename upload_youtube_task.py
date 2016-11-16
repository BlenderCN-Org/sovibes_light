import json
import os

from celery import Celery
from oauth2client.tools import argparser

from youtubeclient import get_authenticated_service
from youtubeclient import upload_vibe


app = Celery('upload_youtube_task',broker='amqp://guest@localhost//')


def create_snippet_from_vibe_description_file(vibe_description_file_path,article_workspace):
    snippet_data = dict()
    with open(vibe_description_file_path) as desc_file:
        json_data= json.load(desc_file)
        description = 'To read full article go on : \n'
        pattern_description = '\n\nSovibes is an application that transforms articles of the web into' + \
                ' video summaries.\n' +\
                'If you want your daily news brought to you in a new way, please subscribe to the channel.\n' + \
                'If you have any remarks on the quality of the videos, please comment. Be sure it will be taking into account.'
        if json_data.get('cdnAmpUrl'):
            description += json_data['cdnAmpUrl'] + pattern_description

        elif json_data.get('href'):
            description+= json_data['href'] +pattern_description

        snippet_data = dict(snippet=dict(title=json_data['title'],
                                      description=description,
                                      tags=json_data['keywords'],
                                      categoryId='22'
                                      ),
                         status=dict(privacyStatus='private'),
                        vibeFilePath=json_data['encodedVibeFilePath']
                         )
    snippet_file_path = article_workspace + '/snippet.json'
    with open(snippet_file_path,'w')  as json_file:
        json.dump(snippet_data,json_file,indent=2,sort_keys=True)
    return snippet_file_path



@app.task
def upload_vibe_to_youtube(vibe_description_file_path,article_workspace):

    youtube = get_authenticated_service()
    print(youtube)
    snippet_file_path = create_snippet_from_vibe_description_file(vibe_description_file_path,article_workspace)
    print('1')
    if os.path.exists(snippet_file_path):
        print('1')
        upload_vibe(youtube,snippet_file_path)

        return True
    else:
        print('Impossible to upload file to youtube snippet missing')
        return False
