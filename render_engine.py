import json
import os
import subprocess

from os.path import isfile, join
from random import randint

from audio_utils import get_audio_duration
from ffmpeg_utils import get_video_duration_in_sec
from json_utils import update_json_file
def render(blender_file_path,python_file_path,input_file_path, output_file_path):
    cmd = 'blender -b ' + \
          '"' + blender_file_path + '" ' + \
          '-P ' + python_file_path + \
          ' -- ' + '"' + input_file_path + '" ' + \
          '--ouput ' + + '"' + output_file_path + '"'
    pass



def render_intro(article, vibe_desciption_file_path, article_workspace):


    # Render text layer
    text_layer_file_path = article_workspace + '/' + article['title'] + '_intro_text_layer.mp4'
    cmd_render_text_layer = 'blender -b ' + os.getcwd() + '/blender_elements/blender_files/intro/pattern_intro_layer_horizontal_default.blend -P render_text_layer.py -- ' \
          + '"' + vibe_desciption_file_path \
          + '" --output ' \
          + '"' + text_layer_file_path + '"'
    try:
        with open(article_workspace + '/render_intro_text_layer_log.txt', 'w') as renderLogFile:
            # render.delay(cmd)
            print(cmd_render_text_layer)
            subprocess.call(cmd_render_text_layer, shell=True,stdout=renderLogFile, stderr=subprocess.PIPE)

        duration = get_video_duration_in_sec(text_layer_file_path)
        title_text_layer_info = dict(filePath=text_layer_file_path,
                          duration=duration)
        update_json_file(vibe_desciption_file_path, 'titleTextLayer', title_text_layer_info)

    except:
        print('Rendering Failed')

    # -----------------------
    # Render intro slideshow pattern_intro_slideshow_vertical_default.blend
    # ------------------------
    intro_slideshow_file_path = article_workspace + '/intro_slideshow.mp4'
    cmd_render_intro_slideshow = 'blender -b ' + os.getcwd() + '/blender_elements/blender_files/intro/pattern_intro_slideshow_default.blend -P render_intro_slideshow.py -- ' \
                            + '"' + vibe_desciption_file_path \
                            + '" --output ' \
                            + '"' + intro_slideshow_file_path + '"'
    try:
        with open(article_workspace + '/render_intro_slideshow_log.txt', 'w') as renderLogFile:
            # render.delay(cmd)
            print(cmd_render_intro_slideshow)
            subprocess.call(cmd_render_intro_slideshow, shell=True, stdout=renderLogFile, stderr=subprocess.PIPE)

        duration = get_video_duration_in_sec(intro_slideshow_file_path)
        title_intro_slide_info = dict(filePath=intro_slideshow_file_path,
                                     duration=duration)
        update_json_file(vibe_desciption_file_path, 'introSlideshow', title_intro_slide_info)

    except:
        print('Rendering Failed')



    # Blend the file together
    intro_file_path = article_workspace + '/intro_vibe.mp4'
    cmd = 'blender -b ' + os.getcwd() + '/blender_elements/blender_files/intro/intro_blend_horizontal.blend -P render_blend_intro.py -- ' \
          + '"' + vibe_desciption_file_path \
          + '" --output ' \
          + '"' + intro_file_path + '"'
    try:
        with open(article_workspace + '/render_blend_intro_log.txt', 'w') as renderLogFile:
            # render.delay(cmd)
            print(cmd)
            subprocess.call(cmd, shell=True, stdout=renderLogFile,stderr=subprocess.PIPE)

        duration = get_video_duration_in_sec(intro_file_path)
        intro_info = dict(filePath=intro_file_path,
                          duration=duration)
        update_json_file(vibe_desciption_file_path, 'introVibe', intro_info)

    except:
        print('Rendering Failed')
    return True


def render_slideshow(article, vibe_desciption_file_path, article_workspace):
    slideshow_file_path = article_workspace + '/' + article['title'] + '_slide.mp4'
    cmd = 'blender -b ' + os.getcwd() + '/blender_elements/blender_files/slideshow/pattern_slideshow.blend -P render_slideshow.py -- ' \
          + '"' + vibe_desciption_file_path \
          + '" --output ' \
          + '"' + slideshow_file_path + '"'
    try:
        with open(article_workspace + '/render_slideshow_log.txt', 'w') as renderLogFile:
            # render.delay(cmd)
            print(cmd)
            subprocess.call(cmd, shell=True, stdout=renderLogFile, stderr=subprocess.PIPE)
        duration = get_video_duration_in_sec(slideshow_file_path)
        slide_info = dict(filePath=slideshow_file_path,
                          duration=duration)
        update_json_file(vibe_desciption_file_path, 'slideVibe', slide_info)

    except:
        print('Rendering slideshow Failed')
    return True


def get_random_background_music(random):
    pass


def video_edit_vibe(article, vibe_desciption_file_path, article_workspace):
    # background_music_file_path = get_random_background_music(random)

    return True




def render_stitch_vibe(article, vibe_desciption_file_path, article_workspace):
    # TODO Choose background music randomly
    background_audio_directory = os.getcwd() + '/blender_elements/sound_background/default'
    background_audio_files = [join(background_audio_directory,f) for f in os.listdir(background_audio_directory) if isfile(join(background_audio_directory, f))]
    background_audio_vibe_file_path = background_audio_files[randint(0,len(background_audio_files)-1)]
    background_audio_duration = get_audio_duration(background_audio_vibe_file_path)
    audio_info = dict(filePath=background_audio_vibe_file_path,
                      duration=background_audio_duration)
    update_json_file(vibe_desciption_file_path,'backgroundAudio',audio_info)
    vibe_path = article_workspace + '/vibe.mp4'
    cmd = 'blender -b ' + os.getcwd() + '/blender_elements/blender_files/intro/intro_blend_horizontal.blend -P render_stitch_vibe.py -- ' \
          + '"' + vibe_desciption_file_path \
          + '" --output ' \
          + '"' + vibe_path + '"'
    try:
        # render.delay(cmd)
        with open(article_workspace + '/render_stitch_log.txt', 'w') as renderLogFile:
            print(cmd)
            subprocess.call(cmd, shell=True, stdout=renderLogFile, stderr=subprocess.PIPE)

        duration = get_video_duration_in_sec(vibe_path)
        vibe_info = dict(filePath=vibe_path,
                          duration=duration)
        update_json_file(vibe_desciption_file_path, 'vibe', vibe_info)

    except:
        print('Rendering slideshow Failed')
    return True





def render_vibe(article, vibe_desciption_file_path, article_workspace):
    # Temporary direction for blender render intermediate files
    tmp_blender_directory = article_workspace + '/blender_result_tmp'
    if not os.path.exists(tmp_blender_directory):
        os.makedirs(tmp_blender_directory)
    # Analyze desc file to get number of media
    print('     RENDERING INTRO')
    if render_intro(article, vibe_desciption_file_path, article_workspace):
        # return True
        print('     RENDERING SLIDESHSOW')
        if render_slideshow(article, vibe_desciption_file_path, article_workspace):
            # return True
            print('     STITCHING INTRO & SLIDESHOW')
            if render_stitch_vibe(article, vibe_desciption_file_path, article_workspace):
                 return True
    # TODO remove temp blender render intermediate files

    pass


    # cmd = 'blender /home/belgaloo/SoVibes/blender/pattern_intro_vertical_1.blend -P render_intro.py -- ' \
    #           + '"' + os.getcwd() + '/vibe_workspace/vibes/Opinion: Who won the debate?/description_file.json' \
    #           + '" --output ' \
    #           + '"' + os.getcwd() \
    #           + '/vibe.mp4"'
    # try:
    #     # render.delay(cmd)
    #     print(cmd)
    #     subprocess.call(cmd,shell=True, stderr=subprocess.PIPE)
    # except:
    #     print('Rendering Failed')
    #
    # pass
