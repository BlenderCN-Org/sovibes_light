from time import sleep

from audio_utils import get_audio_duration
from json_utils import update_json_file
from yvona_client import *
import json


def text_to_speech(directory_dest, vibe_description_file_path):
    with open(vibe_description_file_path) as desc_file:
        json_data = json.load(desc_file)
        audio_data = []
        # TTS title
        tts_title_file_path = directory_dest+ '/title.mp3'
        stringToVoice(json_data['title'],tts_title_file_path)
        title_audio_duration = get_audio_duration(tts_title_file_path)
        audio_info = dict(content=json_data['title'],
                          filePath=tts_title_file_path,
                          duration=title_audio_duration)
        audio_info_title = {'title':audio_info}
        audio_data.append(audio_info_title)

        summary_audio_file_path_list= []
        i = 0
        print('     TTS summmary sentence number : ' + str(len(json_data['summary'])))
        for sentence in json_data['summary']:
            print('     TTS summmary sentence : ' + sentence)
            summary_file_path = directory_dest+'/audio_summary['+str(i)+'].mp3'
            stringToVoice(sentence,summary_file_path)
            summary_audio_file_path_list.append(summary_file_path)
            audio_duration = get_audio_duration(summary_file_path)
            audio_info = dict(content=sentence,
                              filePath=summary_file_path,
                              duration=audio_duration,
                              order=i)
            audio_summary_info = {'summary':audio_info}
            audio_data.append(audio_summary_info)
            i += 1

        if audio_data:
            del json_data['summary']
            update_json_file(vibe_description_file_path,'audios',audio_data)

    return summary_audio_file_path_list


