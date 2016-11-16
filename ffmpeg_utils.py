import json
import os
import subprocess

import re

def encode_to_mp4(source_file_path):
    dest_file_path = ''
    if os.path.exists(source_file_path):
        dir_name = os.path.dirname(source_file_path)
        file_name = os.path.splitext(os.path.basename(source_file_path))[0] + '_encoded.mp4'
        dest_file_path = os.path.join(dir_name,file_name)
        cmd = 'ffmpeg -i ' + \
            '"' + source_file_path +'"' +\
            ' -strict -2 ' + \
            '"' + dest_file_path + '"'

        try:
            print('ENCODING TO MP4 IN PROGRESS')
            subprocess.call(cmd,shell=True,stderr=subprocess.PIPE)
            print('ENCODING TO MP4 COMPLETE')

        except:
            print('Impossible to encode video to mp4')
            dest_file_path = ''
            return dest_file_path
    else:
        print('File does not exist')
        return dest_file_path
    return dest_file_path

def gif_to_mp4(gif_file_path,mp4_file_path):
    cmd = 'ffmpeg -f gif -i '+ \
            '"' + gif_file_path + '" ' + \
            '"' + mp4_file_path + '"'
    try:
        subprocess.call(cmd,shell=True, stderr=subprocess.PIPE)
    except:
        print('Impossible to transform gif')

    return True
# -------------------------------------------------------
# Get the duration from our input string and return a
# dictionary of hours, minutes, seconds
# -------------------------------------------------------
def search_for_duration (ffmpeg_output):

    pattern = re.compile(r'Duration: ([\w.-]+):([\w.-]+):([\w.-]+),')
    match = pattern.search(ffmpeg_output)

    if match:
        hours = match.group(1)
        minutes = match.group(2)
        seconds = match.group(3)
    else:
        hours = minutes = seconds = 0

    # return a dictionary containing our duration values
    return {'hours':hours, 'minutes':minutes, 'seconds':seconds}

# -----------------------------------------------------------
# Get the dimensions from the specified file using ffmpeg
# -----------------------------------------------------------
def get_FFMPEGInfo (file_path):

    p = subprocess.Popen(['ffmpeg', '-i', file_path],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stderr

# -----------------------------------------------------------
# Get the duration by pulling out the FFMPEG info and then
# searching for the line that contains our duration values
# -----------------------------------------------------------
def get_video_duration (file_path):

    ffmpeg_output = get_FFMPEGInfo (file_path)
    return search_for_duration (str(ffmpeg_output))

def get_video_duration_in_sec(file_path):
    duration = get_video_duration(file_path)
    return float(duration['hours']) * 3600 + float(duration['minutes']) * 60 + float(duration['seconds'])


def get_video_metadata(file_path):
    if not os.path.exists(file_path):
        try:
            raise FileExistsError('File @ ' + file_path + ' does not exist')
        except FileExistsError:
            return ''
    result = subprocess.check_output('ffprobe -v quiet -print_format json -show_format -show_streams ' + '"' +file_path + '"' ,shell=True)

    # print(str(result,'utf-8'))
    return str(result,'utf-8')

def get_video_frame_rate(file_path):
    try:
        result = json.loads(get_video_metadata(file_path))
    except:
        return None
    if result.get('streams'):
        for stream in result['streams']:
            if stream.get('codec_type'):
                if stream['codec_type'] == 'video':
                    r_frame_rate = stream['r_frame_rate'].split('/')
                    print('video frame rate : ' + str(int(r_frame_rate[0])/int(r_frame_rate[1])))
                    return int(r_frame_rate[0])/int(r_frame_rate[1])

def get_video_dimensions(file_path):
    try:
        result = json.loads(get_video_metadata(file_path))
    except:
        return [None, None]
    if result.get('streams'):
        for stream in result['streams']:
            if stream.get('codec_type'):
                if stream['codec_type'] == 'video':
                    dimensions = [int(stream['coded_width']),int(stream['coded_height'])]
                    print('Video dimensions are : width : ' + str(dimensions[0]) + ' height : ' + str(dimensions[1]))
                    return dimensions
