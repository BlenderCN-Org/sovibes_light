from newspaper import nlp
from nltk import sent_tokenize, re
from newspaper import Article
from json_utils import update_json_file

from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.html import HtmlParser
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.utils import get_stop_words
from pymediainfo import MediaInfo
import os

from download_utils import url_file_exists


def get_media_info(file_path):
    if not os.path.isfile(file_path):
        if not url_file_exists(file_path):
            print('Impossible to get media info for file : \n' + str(file_path))
            return {}
    media_info = MediaInfo.parse(file_path)


    media_tracks_info = []
    for track in media_info.tracks:
        media_tracks_info.append(track.to_data())
    media_data = dict(tracks=media_tracks_info)
    return media_data


def get_general_track_info(file_path):
    media_data = get_media_info(file_path)
    for track in media_data['tracks']:
        if track['track_type'] == 'General':
            return track
    return {}


def get_video_track_info(file_path):
    media_data = get_media_info(file_path)
    if media_data.get('tracks'):
        for track in media_data['tracks']:
            if track['track_type'] == 'Video':
                return track
    return {}


def get_audio_track_info(file_path):
    media_data = get_media_info(file_path)
    for track in media_data['tracks']:
        if track['track_type'] == 'Audio':
            return track
    return {}


def get_video_frame_rate(file_path):
    track = get_video_track_info(file_path)
    if track.get('frame_rate'):
        return track['frame_rate']
    else:
        return ''