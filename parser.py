import json
import os

import re
import subprocess
from urllib import *

from bs4 import BeautifulSoup
from newspaper import Article

from feedlyclient import *
from image_utils import get_image_url_size


# -----------------------------------------------------
# Get only the feeds with amp and full articles
# -----------------------------------------------------
def get_amp_and_full_content_feeds(json_file_path):
    amp_fullcontent_feeds = []
    try:
        with open(json_file_path) as jsonFeedsFile:
            json_feeds_data = json.load(jsonFeedsFile)
            for feed in json_feeds_data:
                if feed.get("amp") and feed.get("fullContent"):
                    if feed["amp"] == 'true' and feed["fullContent"] == 'true':
                        amp_fullcontent_feeds.append(feed)

                else:
                    print('Feed : ' + feed["title"] + ' missing amp or fullContent parameter')

    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))

    return amp_fullcontent_feeds


# -----------------------------------------------------
# Get only the feeds with amp articles
# -----------------------------------------------------
def get_amp_feeds(json_file_path):
    amp_feeds = []
    try:
        with open(json_file_path) as jsonFeedsFile:
            json_feeds_data = json.load(jsonFeedsFile)
            for feed in json_feeds_data:
                if feed.get("amp"):
                    if feed["amp"] == 'true':
                        amp_feeds.append(feed)

                else:
                    print('Feed : ' + feed["title"] + ' missing amp or fullContent parameter')

    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))

    return amp_feeds

# -----------------------------------------------------
# Get only the feeds with amp articles
# -----------------------------------------------------
def get_feeds_from_file(json_file_path):
    feeds = []
    try:
        with open(json_file_path) as jsonFeedsFile:
            json_feeds_data = json.load(jsonFeedsFile)
            for feed in json_feeds_data:
                feeds.append(feed)
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))

    return feeds


def get_amp_body_content(article_html):
    amp_content = None
    soup = BeautifulSoup(article_html)
    amp_content = soup.find('div', {'class': 'post-content'})
    if amp_content == None:
        amp_content = soup.find('main', {'class': 'content'})
        if amp_content == None:
            amp_content = soup.find('div', {'class': 'content'})
    return amp_content


# -----------------------------------------------------
# Get image sources from a html string content
# -----------------------------------------------------
def get_list_images_from_article_html(html_content):
    page = BeautifulSoup(html_content)
    images_url = []
    for image in page.findAll('img'):
        # print(image.get('src'))
        images_url.append(image.get('src'))
    return images_url


# -----------------------------------------------------
# Get images sources from the content response of an url
# -----------------------------------------------------
def get_list_images_from_article_url(url):
    temp_html_file = 'temp.html'
    subprocess.call('wget -O ' + temp_html_file + ' "' + url + '"',
                    shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    article_html = ''

    with open(temp_html_file) as tmpHtml:
        article_html = tmpHtml.read()

    soup = BeautifulSoup(article_html)
    amp_content = get_amp_body_content(article_html)
    if amp_content is not None:
        soup = BeautifulSoup(str(amp_content))
    # if 'nytimes' in url:
    #     page = soup.find("article", {"id": "story"})
    #     if page == None:
    #         page = soup.find("div", {"class": "generic-wrap"})
    #         if page == None:
    #             page = soup
    #         # page = soup.select('div.generic-wrap')

    images_url = []
    for image in soup.findAll('img'):
        # print(image.get('src'))
        imageURL = image.get('src')
        try:
            imageSize = get_image_url_size(imageURL)
            if imageSize["width"] > 300 or imageSize["height"] > 300:
                images_url.append(imageURL)
        except:
            # TODO manage exception
            continue

    for image in soup.findAll('amp-img'):
        # print(image.get('src'))
        imageURL = 'https://cdn.ampproject.org' + image.get('src')
        try:
            imageSize = get_image_url_size(imageURL)
            if imageSize["width"] > 300 or imageSize["height"] > 300:
                images_url.append(imageURL)
        except:
            # TODO manage exception
            continue



    for image in soup.findAll('amp-anim'):
        # print(image.get('src'))
        imageURL = 'https://cdn.ampproject.org' + image.get('src')
        try:
            imageSize = get_image_url_size(imageURL)
            if imageSize["width"] > 200 and imageSize["height"] > 200:
                images_url.append(imageURL)
        except:
            # TODO manage exception
            continue

    if os.path.exists(temp_html_file):
        os.remove(temp_html_file)
    return images_url


# -----------------------------------------------------
# Get video sources from the content response of an url
# -----------------------------------------------------
def get_list_videos_from_article_url(url):
    temp_html_file = 'temp.html'
    subprocess.call('wget -O ' + temp_html_file + ' "' + url + '"',
                    shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    articleHtml = ''

    with open(temp_html_file) as tmpHtml:
        articleHtml = tmpHtml.read()

    soup = BeautifulSoup(articleHtml)

    amp_content = get_amp_body_content(articleHtml)
    if amp_content is not None:
        soup = BeautifulSoup(str(amp_content))
    # if 'nytimes' in url:
    #     subprocess.call('wget -O ' + temp_html_file + ' "' + url + '"',
    #                     shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    #     articleHtml = ''
    #     with open(temp_html_file) as tmpHtml:
    #         articleHtml = tmpHtml.read()
    # else:

    videos_url = []
    for video in soup.findAll('video'):
        # print(image.get('src'))
        videoURL = video.get('src')
        videos_url.append(videos_url)
    for video in soup.findAll('amp-iframe'):
        if '.mp4' in video.get('src'):
            temp = re.sub('.*url=', '', video.get('src'))
            temp = re.sub('&.*', '', temp)
            videos_url.append(temp)
    for video in soup.findAll('amp-video'):
        videos_url.append(video.get('src'))

    return videos_url


# -----------------------------------------------------
# Get youtube sources from the content response of an url
# -----------------------------------------------------
def get_list_youtube_video_from_article(url):
    tempHtmlFile = 'temp.html'
    subprocess.call('wget -O ' + tempHtmlFile + ' "' + url + '"',
                    shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    articleHtml = ''

    with open(tempHtmlFile) as tmpHtml:
        articleHtml = tmpHtml.read()

    soup = BeautifulSoup(articleHtml)

    amp_content = get_amp_body_content(articleHtml)
    if amp_content is not None:
        soup = BeautifulSoup(str(amp_content))

    youtube_ids = []
    for link in soup.findAll('a'):
        videoURL = link.get('href')
        if link.get('href') and 'https://www.youtube.com/watch?v' in videoURL:
            youtube_ids.append(videoURL)
    for frame in soup.findAll('iframe'):
        if frame.get('data-recommend-id'):
            youtube_attr = frame.get('data-recommend-id')
            youtube_id = re.sub('.*://', '', youtube_attr)
            youtube_ids.append(youtube_id)
        if frame.get('src'):
            youtube_attr = frame.get('src')
            if 'youtube' in youtube_attr:
                youtube_ids.append(youtube_attr)

    for frame in soup.findAll('amp-youtube'):
        if frame.get('data-videoid'):
            youtube_attr = frame.get('data-videoid')
            already_in_list = False
            if not len(youtube_ids) == 0:
                for youtube_id in youtube_ids:
                    if youtube_attr in youtube_id:
                        already_in_list = True
                        break;
            else:
                youtube_ids.append(youtube_attr)
                already_in_list = True

            if not already_in_list:
                youtube_ids.append(youtube_attr)

    return youtube_ids


def get_number_of_pictures(article):
    if article.get('cdnAmpUrl'):
        return len(get_list_images_from_article_url(article['cdnAmpUrl'])) + len(get_list_videos_from_article_url(article['cdnAmpUrl']))
    if article.get('alternate'):
        if article['alternate'][0].get('href'):
            return len(get_list_images_from_article_url(article['alternate'][0]['href'])) + len(get_list_videos_from_article_url(article['alternate'][0]['href']))


def get_number_of_videos(article):
    if article.get('cdnAmpUrl'):
        return len(get_list_youtube_video_from_article(article['cdnAmpUrl']))
    if article.get('alternate'):
        if article['alternate'][0].get('href'):
            return len(get_list_youtube_video_from_article(article['alternate'][0]['href']))


# Score article by media
def score_article(article):
    score = 0
    score = get_number_of_pictures(article) * 2 + get_number_of_videos(article) * 15
    return score


def get_most_popular_articles(feedList, timeStamp, maxNumber):
    articles_features = []
    articles = []
    for feed in feedList:
        results = json.loads(json.dumps(getStream(feed["feedId"], '40', str(timeStamp), '0')))
        items = results["items"]
        for item in items:
            if item.get('published'):
                if item['published'] < timeStamp:
                    continue
            if item.get('engagement'):
                if get_number_of_videos(item)>0:
                    articles.append(item)
                # for article in items:
                #     articles_features.append({"id": article["id"],"engagement" : article["engagement"], "score" : score_article(article)})

    if len(articles) < maxNumber:
        return articles

    sortedArticle = sorted(articles, key=lambda item: (item["engagement"]), reverse=True)[0:maxNumber]
    return sortedArticle


def get_most_popular_articles_per_topic(listTopicFile, timeStamp, maxNumber):
    articles = []
    maxNumberOfArticlePerTopic = int(maxNumber / len(listTopicFile))
    for topicFile in listTopicFile:
        # Get feed from topic containing amp url
        # feedToVibesify = get_amp_feeds(topicFile)
        feedToVibesify = get_feeds_from_file(topicFile)

        articlesPerTopic = get_most_popular_articles(feedToVibesify, timeStamp, maxNumberOfArticlePerTopic)
        articles.extend(articlesPerTopic)
    return articles


# Parse article and create a json file description to path
def parse(article, article_workspace, feeds_directory):
    descriptionData = {}
    # Source
    descriptionData["origin_title"] = article["origin"]["title"]
    descriptionData["source_visual"] = feeds_directory + '/' + article["origin"]["title"] + '/icon'
    descriptionData["title"] = article["title"]
    if article.get('visual'):
        descriptionData["visual"] = article['visual']

    if article.get('cdnAmpUrl'):
        descriptionData['cdnAmpUrl'] = article['cdnAmpUrl']
        descriptionData["image_urls"] = get_list_images_from_article_url(article['cdnAmpUrl'])
        descriptionData["video_urls"] = get_list_videos_from_article_url(article['cdnAmpUrl'])
        descriptionData["youtube_ids"] = get_list_youtube_video_from_article(article['cdnAmpUrl'])

    elif article.get('alternate'):
        if article['alternate'][0].get('href'):
            descriptionData['href'] = article['alternate'][0]['href']
            descriptionData["image_urls"] = get_list_images_from_article_url(article['alternate'][0]['href'])
            descriptionData["video_urls"] = get_list_videos_from_article_url(article['alternate'][0]['href'])
            descriptionData["youtube_ids"] = get_list_youtube_video_from_article(article['alternate'][0]['href'])

    desc_file_path = article_workspace + '/description_file.json'
    with open(desc_file_path, 'w+') as descFile:
        json.dump(descriptionData, descFile, sort_keys=True, indent=2)

    return desc_file_path
