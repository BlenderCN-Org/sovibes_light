import json
import os


from download_utils import *
from ffmpeg_utils import gif_to_mp4, get_video_metadata, get_video_dimensions, get_video_frame_rate
from ffmpeg_utils import get_video_duration_in_sec
from image_utils import get_image_width, get_image_height, get_image_url_height, get_image_url_width, \
    get_image_url_mime_type, convert_gif_to_jpg
from json_utils import update_json_file, update_json_file_by_key


# -----------------------------------------------------------
# Download all media parsed in the article
# -----------------------------------------------------------
def download_article_media(diretoryArticle, descriptionArticleFilePath):

    jsonArticleData = ''
    with open(descriptionArticleFilePath) as renderJobFile:
        jsonArticleData = json.load(renderJobFile)
    # DOWNLOAD VISUAL
    print('     DOWNLOADING VISUAL')
    if jsonArticleData.get('visual'):
        if jsonArticleData['visual'].get('url'):
            if jsonArticleData['visual']['url'] != 'none':
                visual_url = jsonArticleData['visual']['url']
                image_content_type = get_image_url_mime_type(visual_url)
                if image_content_type == 'image/gif':
                    imageFilePath = diretoryArticle + '/' + os.path.basename(visual_url)
                    download_url_to_file(visual_url, imageFilePath)
                    gif_mp4_file_path = diretoryArticle + '/' + os.path.splitext(os.path.basename(imageFilePath))[
                        0] + '.mp4'
                    gif_to_mp4(imageFilePath, gif_mp4_file_path)
                    update_json_file_by_key(descriptionArticleFilePath, ['visual', 'filePath'], gif_mp4_file_path)
                else:
                    imageFilePath = diretoryArticle + '/' + os.path.basename(visual_url)
                    download_url_to_file(visual_url, imageFilePath)
                    update_json_file_by_key(descriptionArticleFilePath, ['visual','filePath'], imageFilePath)

    print('     DOWNLOADING IMAGES')
    # DOWNLOAD IMAGES
    listImages = []
    if jsonArticleData.get('image_urls'):
        listImages = jsonArticleData["image_urls"]
    images_data = []
    for imageUrl in listImages:
        print('     DOWNLOADING IMAGE URL : ' + imageUrl)
        imageFilePath = diretoryArticle + '/' + os.path.basename(imageUrl)
        download_url_to_file(imageUrl,imageFilePath)

        image_content_type = get_image_url_mime_type(imageUrl)
        # If the image is a gif transform it to mp4
        if image_content_type == 'image/gif':
            gif_mp4_file_path = diretoryArticle + '/' + os.path.splitext(os.path.basename(imageFilePath))[0] + '.mp4'
            if not os.path.exists(gif_mp4_file_path):
                gif_to_mp4(imageFilePath, gif_mp4_file_path)
            gif_mp4_duration = get_video_duration_in_sec(gif_mp4_file_path)
            if gif_mp4_duration>1:
                image_info = dict(url=imageUrl,
                                  FilePath=imageFilePath,
                                  gifMp4FilePath=gif_mp4_file_path,
                                  duration=gif_mp4_duration,
                                  width=get_image_width(imageFilePath),
                                  height=get_image_height(imageFilePath),
                                  contentType=image_content_type)
            else:
                gif_jpg_file_path = diretoryArticle + '/' + os.path.splitext(os.path.basename(imageFilePath))[0] + '.jpg'
                convert_gif_to_jpg(imageFilePath,gif_jpg_file_path)
                image_info = dict(url=imageUrl,
                              FilePath=gif_jpg_file_path,
                              width=get_image_width(gif_jpg_file_path),
                              height=get_image_height(gif_jpg_file_path),
                              contentType='image/jpeg')


        else:
            image_info = dict(url=imageUrl,
                              FilePath=imageFilePath,
                              width=get_image_width(imageFilePath),
                              height=get_image_height(imageFilePath),
                              contentType=image_content_type)

        images_data.append(image_info)

    del jsonArticleData['image_urls']
    update_json_file(descriptionArticleFilePath,'images',images_data)

    print('     DOWNLOADING VIDEOS')
    #DOWNLOAD VIDEOS
    listVideos = []
    list_youtube_videos = []
    if jsonArticleData.get('video_urls'):
        listVideos = jsonArticleData["video_urls"]
    if jsonArticleData.get('youtube_ids'):
        list_youtube_videos = jsonArticleData['youtube_ids']

    videos_data =[]
    for videoUrl in listVideos:
        if videoUrl==None:
            continue
        print('     DOWNLOADING VIDEO URL : ' + videoUrl)
        videoFilePath = diretoryArticle + '/' + os.path.basename(videoUrl)
        download_url_to_file(videoUrl, videoFilePath)
        video_duration = get_video_duration_in_sec(videoFilePath)
        frame_rate = get_video_frame_rate(videoFilePath)
        video_dimensions = get_video_dimensions(videoFilePath)
        video_info = dict(url=videoUrl,
                          duration=video_duration,
                          filePath=videoFilePath,
                          frameRate=frame_rate,
                          width=video_dimensions[0],
                          height=video_dimensions[1])
        videos_data.append(video_info)
    for youtube_video in list_youtube_videos:
        print('     DOWNLOADING VIDEO URL : ' + youtube_video)
        youtube_video_file_path = download_youtube_video(youtube_video, diretoryArticle)
        already_downloaded = False
        for video in videos_data:
            if youtube_video_file_path == video['filePath']:
                already_downloaded=True
                break;
        if not youtube_video_file_path or already_downloaded:
            continue
        video_duration = get_video_duration_in_sec(youtube_video_file_path)
        if video_duration>360:
            continue
        frame_rate = get_video_frame_rate(youtube_video_file_path)
        video_dimensions = get_video_dimensions(youtube_video_file_path)

        video_info = dict(url=youtube_video,
                          duration=video_duration,
                          filePath=youtube_video_file_path,
                          source='youtube',
                          youtube_id=youtube_video,
                          frameRate=frame_rate,
                          width=video_dimensions[0],
                          height=video_dimensions[1])
        videos_data.append(video_info)

    del jsonArticleData['youtube_ids']
    del jsonArticleData['video_urls']
    update_json_file(descriptionArticleFilePath,'videos',videos_data)

    return True