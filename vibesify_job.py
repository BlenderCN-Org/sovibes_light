import os
import json

from oauth2client.tools import argparser

from downloader import download_article_media
from ffmpeg_utils import encode_to_mp4
from json_utils import update_json_file
from parser import *
from render_engine import render_vibe
from tts_engine import text_to_speech
from upload_youtube_task import upload_vibe_to_youtube
from vibesify_beat_config import *
import datetime
import time
from download_utils import download_url_to_file
from summarizer import summarize_article
from youtubeclient import get_authenticated_service

NEWS_FEEDS_JSON_FILE_PATH = os.getcwd() + '/news_sites_list.json'
TECHNOLOGY_FEEDS_JSON_FILE_PATH = os.getcwd() + '/technology_sites_list.json'
GAMING_FEEDS_JSON_FILE_PATH = os.getcwd() + '/gaming_sites_list.json'
FASHION_FEEDS_JSON_FILE_PATH = os.getcwd() + '/fashion_sites_list.json'
FOOD_FEEDS_JSON_FILE_PATH = os.getcwd() + '/food_sites_list.json'
CELEBRITY_FEEDS_JSON_FILE_PATH = os.getcwd() + '/celebrity_sites_list.json'
CHINESE_FEEDS_JSON_FILE_PATH = os.getcwd() + '/chinese_sites_list.json'

JOB_LOG_JSON_FILE_PATH = os.getcwd() + '/job_log.json'

FEED_WORSKSPACE = os.getcwd() + '/vibe_workspace/feeds'
VIBE_WORSKSPACE = os.getcwd() + '/vibe_workspace/vibes'


# -----------------------------------------------------
# Get last job launch time
# -----------------------------------------------------
def get_last_job_timestamp(job_log_json_file_path):
    with open(job_log_json_file_path) as jobLogFile:
        json_job_log_data = json.load(jobLogFile)
        return json_job_log_data["jobs"][0]["timeStamp"]


# -----------------------------------------------------
# Update job log file with latest information
# -----------------------------------------------------
def update_job_log(job_log):
    try:
        new_jobs = []
        # TODO use json utils to update file
        # Open job json file for update
        with open(JOB_LOG_JSON_FILE_PATH) as jobLogFile:
            json_job_log_file = json.load(jobLogFile)
            json_job_log_file["jobs"].insert(0, job_log)
            new_jobs = json_job_log_file
        with open(JOB_LOG_JSON_FILE_PATH, 'w') as jobLogFile:
            json.dump(new_jobs, jobLogFile, indent=2)
        return True
    except:
        print('Impossible to update job log file')
        return False


# -----------------------------------------------------
# Create directory for feed elements
# -----------------------------------------------------
def create_feed_workspace(list_topic_files):
    # Create feed directory
    if not os.path.exists(FEED_WORSKSPACE):
        os.makedirs(FEED_WORSKSPACE)
    # For each topic composed of feeds we create the directory
    # and download the icon
    for topicFile in list_topic_files:
        with open(topicFile) as jsonFeedsFile:
            json_feeds_data = json.load(jsonFeedsFile)
            for feed in json_feeds_data:
                feed_path = FEED_WORSKSPACE + '/' + feed["title"]
                # If path already exist continue else create directory, download and create feed data file
                if os.path.exists(feed_path):
                    continue
                else:
                    os.makedirs(feed_path)
                    if feed.get('visualUrl'):
                        try:
                            download_url_to_file(feed['visualUrl'], feed_path + '/icon')
                        except IOError:
                            print('Impossible to download feed icon')
                        with open(feed_path + '/feed.json', 'w+') as feedFile:
                            feedFile.write(json.dumps(feed, indent=2))

    return True


# -----------------------------------------------------
# Create directory for an article where all the elements
# for the vibe will be stored
# -----------------------------------------------------
def create_vibe_workspace(article):
    vibe_path = VIBE_WORSKSPACE + '/' + article['title']
    if not os.path.exists(vibe_path):
        os.makedirs(vibe_path)

    return vibe_path

def vibesify_article(article):
    pass





# -----------------------------------------------------
# THIS IS WHERE THE MAGIC HAPPENS
# -----------------------------------------------------
def vibesify(job_time_stamp):

    now = time.mktime(datetime.datetime.now().timetuple()) * 1e3
    time_stamp = get_last_job_timestamp(JOB_LOG_JSON_FILE_PATH)
    #, FASHION_FEEDS_JSON_FILE_PATH,FOOD_FEEDS_JSON_FILE_PATH
    # Get Feeds and create workspace
    list_topic_feeds_files = [ NEWS_FEEDS_JSON_FILE_PATH,TECHNOLOGY_FEEDS_JSON_FILE_PATH, CELEBRITY_FEEDS_JSON_FILE_PATH, GAMING_FEEDS_JSON_FILE_PATH]
    # list_topic_feeds_files = [CHINESE_FEEDS_JSON_FILE_PATH]
    # list_topic_feeds_files = [GAMING_FEEDS_JSON_FILE_PATH]
    create_feed_workspace(list_topic_feeds_files)

    article_to_vibesify = get_most_popular_articles_per_topic(list_topic_feeds_files, time_stamp,
                                                              MAX_NUMBER_VIBES_PER_JOB)
    feeds_directory = os.getcwd() + '/vibe_workspace/feeds'
    number_article_vibesified = len(article_to_vibesify)
    print('Render Job contains ' + str(number_article_vibesified) + ' to vibesify')

    for article in article_to_vibesify:
        print('VIBESIFY article : ' + article['title'])
        if article.get('cdnAmpUrl'):
            print('Article @ : ' + article['cdnAmpUrl'])
        elif article.get('alternate'):
            if article['alternate'][0].get('href'):
                print('Article @ : ' + article['alternate'][0]['href'])
        vibe_path = VIBE_WORSKSPACE + '/' + article['title']
        if os.path.exists(vibe_path):
            continue


        article_workspace = create_vibe_workspace(article)
        print('Creation article workspace COMPLETE @' + article_workspace)

        # In case the article has been already vibesified
        if os.path.exists(article_workspace + '/render_job.json'):
            with open(article_workspace + '/render_job.json') as renderJobFile:
                json_data = json.load(renderJobFile)
                if json_data['render_status'] == 'RENDER_COMPLETE':
                    number_article_vibesified -= 1
                    print('Article already Vibesified @' + article_workspace)
                    continue
        # Parse article to get media
        print('Article PARSING in progress')
        vibe_description_file_path = parse(article, article_workspace, feeds_directory)
        print('Article PARSING COMPLETE')

        # Download all media from article to workspace to vibesify
        print('DOWNLOADING article Media in progress')
        try:
            download_article_media(article_workspace, vibe_description_file_path)
        except:
            # TODO manage in function the exception
            print('Download problem')
        print('DOWNLOADING article Media COMPLETE')

        print('SUMMARIZING article in progress')
        summarized = summarize_article(article, vibe_description_file_path)
        print('SUMMARIZING article COMPLETE')
        if not summarized:
            print(
                'Failed to summarize article : ' + article['title'] + ' @ url : ' + article['alternate'][0]['href'])
            continue

        print('TEXT TO SPEECH article summary in progress')
        text_to_speech(article_workspace, vibe_description_file_path)
        print('TEXT TO SPEECH article summary COMPLETE')

        print('RENDER vibe in progress')
        render_vibe(article, vibe_description_file_path, article_workspace)
        print('RENDER vibe COMPLETE')

        vibe_file_path=''
        with open(vibe_description_file_path) as desc_file:
            json_data = json.load(desc_file)
            vibe_file_path = json_data['vibe']['filePath']
        if os.path.exists(vibe_file_path):
            encoded_vibe_file_path = encode_to_mp4(vibe_file_path)
            update_json_file(vibe_description_file_path,'encodedVibeFilePath',encoded_vibe_file_path)
            upload_vibe_to_youtube.delay(
                vibe_description_file_path,
                article_workspace)
        # upload_vibe_to_youtube(vibe_description_file_path)

    # except:
        # print('Render Job FAILED')
        # jobLog = dict(timestamp=now,
        #               status='FAILED',
        #               numberOfVibes=number_article_vibesified)
        # update_job_log(jobLog)
        # return False

    # jobLog = dict(timestamp=now,
    #               status='COMPLETE',
    #               numberOfVibes=number_article_vibesified)
    # update_job_log(jobLog)

    return True

now = datetime.datetime.now()
then = now - datetime.timedelta(hours=3)
timestamp = time.mktime(then.timetuple()) * 1e3
vibesify(timestamp)
