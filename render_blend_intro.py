import argparse
import json
import os
import urllib
from math import tan

import bpy
import sys
sys.path.append(os.getcwd()+'/')
print(sys.path)
from blender_utils import *


# -----------------------------------------------------------------------------------
# Get the length of the slideshow given the duration of each summary audio sentences
# -----------------------------------------------------------------------------------
def get_duration_slideshow(json_data):
    duration = 0
    summary_list = get_summary_list(json_data)
    for sentence in summary_list:
        if sentence.get('summary'):
            if sentence['summary'].get('duration'):
                duration += sentence['summary']['duration']
    return duration


# ---------------------------------------------
# Get only summary sentence, taking away title
# ---------------------------------------------
def get_summary_list(json_data):
    summary_list = []
    for sentence in json_data:
        if not sentence.get('title'):
            summary_list.append(sentence)
    return summary_list


# -------------------------------------------------------------------
# Calculate the display duration of each still image taking away GIF
# -------------------------------------------------------------------
def calculate_length_per_image(scene_duration, images):
    # count no gif images
    count = 0
    for image in images:
        if not image['contentType'] == 'image/gif':
            count += 1
        else:
            scene_duration-= image['duration'] * get_scene_render_fps()

    return math.ceil(scene_duration / count)


# --------------------------------
# Scale image to fi camera frame
# --------------------------------
def scale_image_to_fit_frame(camera, image_object):
    scene = bpy.context.scene
    print(scene)
    ratio_camera = scene.render.resolution_x / scene.render.resolution_y
    print('Ration Camera : ' + str(ratio_camera))

    camera_field_of_view = camera.data.angle
    # init
    # Case when width and height are equal
    #   -------
    #   |     |
    #   |     |
    #   -------
    camera_fov_horizontal_half = camera_field_of_view / 2
    camera_fov_vertical_half = camera_field_of_view / 2

    print('cam FOV : ' + str(camera_field_of_view))

    # Case when width camera smaller than height
    #   -----
    #   |   |
    #   |   |
    #   |   |
    #   -----
    if ratio_camera < 1:
        camera_fov_horizontal_half = camera_field_of_view / 2
        print('camera_fov_horizontal_half : ' + str(camera_fov_horizontal_half))
        print(camera_fov_horizontal_half)
        camera_fov_horizontal_half *= ratio_camera
        print('camera_fov_horizontal_half : ' + str(camera_fov_horizontal_half))
        camera_fov_vertical_half = camera_field_of_view / 2
        print('camera_fov_vertical_half : ' + str(camera_fov_vertical_half))

    # Case when width camera is greater than height
    #   ___________
    #   |         |
    #   |         |
    #   -----------
    elif ratio_camera > 1:
        camera_fov_vertical_half = camera_field_of_view / 2
        camera_fov_vertical_half *= ratio_camera
        camera_fov_horizontal_half = camera_field_of_view / 2
        print(camera_fov_horizontal_half)

    scale_ratio = get_scale_ratio(image_object)
    if get_plane_ratio(image_object) > 1:
        image_object.dimensions.x = 2 * tan(camera_fov_horizontal_half) * image_object.location.y + 0.03
        scene.update()
        scaleXYRatioObject(image_object, scale_ratio)
    else:
        image_object.dimensions.y = 2 * tan(camera_fov_vertical_half) * image_object.location.y
        scaleXYRatioObject(image_object, scale_ratio)

# ---------------------------------------------
# Get only title sentence data
# ---------------------------------------------
def get_title_data(json_data):
    for sentence in json_data:
        if sentence.get('title'):
            return sentence


def init_scene(args):
    # try:

    bpy.ops.object.select_all(action='DESELECT')
    jsonDescriptionFilePath = os.path.abspath(args.input)
    with open(jsonDescriptionFilePath) as blender_data_file:
        blender_data = json.load(blender_data_file)

        # ---------------------------
        # Init scene duration
        # ---------------------------
        area = find_sequence_editor_area()
        duration_fps = 0
        title_data ={}
        if blender_data.get('audios'):
            title_data = get_title_data(blender_data['audios'])
            print(title_data)
            duration_fps = title_data['title']['duration'] * get_scene_render_fps()
            set_scene_frame_end(duration_fps)
            # Add sound strip


        else:
            print('No summary impossible to vibesify')
            pass

        # Add title audio strip
        bpy.ops.sequencer.sound_strip_add({'area': area}, filepath=title_data['title']['filePath'],
                                          frame_start=0, channel=1)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        duration = active_strip.frame_final_duration
        # Add intro slideshow movie strip
        bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=blender_data['introSlideshow']['filePath'],
                                          frame_start=0, channel=2)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        active_strip.frame_final_duration = duration
        # Add intro text layer movie strip
        bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=blender_data['titleTextLayer']['filePath'],
                                          frame_start=0, channel=3)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        active_strip.blend_type = 'ALPHA_OVER'
        active_strip.frame_final_duration = duration

    # except:
    #     print('Impossible to init slideshow scene')
    pass


def renderScene(args):
    # Initialize scene/camera
    scene = bpy.context.scene
    scene.frame_start = 1
    # scene.frame_end = args.fps * args.time
    scene.render.image_settings.file_format = args.file_format
    scene.render.ffmpeg.codec = args.codec
    scene.render.ffmpeg.format = args.format
    scene.render.filepath = args.output
    print(args.output)
    bpy.ops.render.render(animation=True, write_still=True)
    pass


class ArgumentParserError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(message)
        raise ArgumentParserError(message)


parser = ThrowingArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    'input',
    help="Article json description")
parser.add_argument(
    '-o', '--output', default='/tmp/',
    help="Output file")
parser.add_argument(
    '-r', '--resolution', default='1080x1920',
    help="Output resolution width x height")
parser.add_argument(
    '--fps', type=int, default=24,
    help="Frame per second")
parser.add_argument(
    '-t', '--time', type=int, default='5',
    help="Duration of the video in second")
parser.add_argument(
    '-ff', '--file-format', default='FFMPEG',
    help="Blender file format")
parser.add_argument(
    '-f', '--format', default='MPEG4',
    help="Blender format")
parser.add_argument(
    '-c', '--codec', default='MPEG4',
    help="Blender codec")

if '--' in sys.argv:
    argv = sys.argv
    sys.argv = [' '.join(argv[:argv.index('--')])] + argv[argv.index('--') + 1:]
else:
    sys.argv = [' '.join(sys.argv)]

try:
    init_scene(parser.parse_args())
    renderScene(parser.parse_args())
except ArgumentParserError:
    pass
except SystemExit:
    pass
