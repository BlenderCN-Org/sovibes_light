import argparse
import json
import os
import urllib
from math import tan

import bpy
import sys
sys.path.append(os.getcwd()+'/')
print(sys.path)
bpy.ops.wm.addon_enable(module="io_import_images_as_planes")
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
    count=0
    if not images :
        count = 1
    for image in images:
        if not image['contentType'] == 'image/gif':
            count += 1
        # else:
        #     scene_duration-= image['duration'] * get_scene_render_fps()
    print('number of img ' + str(count))
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


def init_scene(args):
    # try:

    bpy.ops.object.select_all(action='DESELECT')
    jsonDescriptionFilePath = os.path.abspath(args.input)
    with open(jsonDescriptionFilePath) as blender_data_file:
        blender_data = json.load(blender_data_file)

        # ---------------------------
        # Init scene duration
        # ---------------------------
        summary_data = []
        duration_fps = 0
        if blender_data.get('audios'):
            summary_data = get_summary_list(blender_data['audios'])
            duration_fps = get_duration_slideshow(summary_data) * get_scene_render_fps()
            set_scene_frame_end(duration_fps)

        else:
            print('No summary impossible to vibesify')
            pass

        # ---------------------------
        # Create sentence text object
        # ---------------------------
        frame_start = 0
        for sentence in summary_data:
            sentence_content = sentence['summary']['content']
            sentence_content = ''.join(
                formatString(sentence_content, len(bpy.data.objects["@sentence_dummy"].data.body)))
            sentenceObject = duplicateObject(bpy.data.objects["@sentence_dummy"])
            setTextContent(sentenceObject, sentence_content)
            bpy.context.scene.update()
            fitTextDimension(sentenceObject, bpy.data.objects['@sentence_bounding_box'])
            frame_end = sentence['summary']['duration'] * get_scene_render_fps()
            frame_end += frame_start
            move_object_keyframes(frame_start, frame_end, sentenceObject)
            # Add sound strip
            area = find_sequence_editor_area()
            bpy.ops.sequencer.sound_strip_add({'area': area}, filepath=sentence['summary']['filePath'],
                                              frame_start=frame_start, channel=2)
            frame_start += sentence['summary']['duration'] * get_scene_render_fps()
            sentenceObject.hide_render = False

        # Add sentence camera as scene strip
        area = find_sequence_editor_area()
        bpy.ops.sequencer.scene_strip_add({'area': area}, frame_start=0, channel=1)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        active_strip.scene_camera = bpy.data.objects['camera_text']
        active_strip.blend_type = 'ALPHA_OVER'

        # -------------
        # create image
        # -------------
        frame_start = 0
        frame_end = 0

        length_per_image = calculate_length_per_image(get_scene_frame_end(), blender_data['images'])
        print('scene frame end ' + str(get_scene_frame_end()))
        print('length per image ' + str(length_per_image))
        images = blender_data['images']
        x_location_cam = 2

        if len(images)>0:
            print('image')
            for image in images:
                image_file_path = ''
                # Place image in front of camera
                if not image['contentType'] == 'image/gif':
                    image_file_path = image['FilePath']
                    print(image_file_path)
                    frame_end = frame_start + length_per_image
                else:
                    # TODO get video length to calculate frame_end for gif
                    continue
                    image_file_path = image['gifMp4FilePath']
                    frame_end = frame_start + image['duration']

                camera_object = bpy.data.objects['Camera']
                new_camera = duplicateObject(camera_object)
                new_camera.location.x = x_location_cam
                bpy.context.scene.update()

                image_object = createImageAsPlane(image_file_path,
                                                  location=(new_camera.location.x, 1.0, new_camera.location.z))
                scale_image_to_fit_frame(new_camera, image_object)
                x_location_cam += 2

                # Create scene strip
                print('frame_end ' + str(frame_end))
                bpy.ops.sequencer.scene_strip_add({'area': area}, frame_start=frame_start)
                active_strip = bpy.context.scene.sequence_editor.active_strip
                print('Strip ')
                print(active_strip)
                active_strip.scene_camera = new_camera
                active_strip.blend_type = 'ALPHA_UNDER'
                active_strip.frame_final_duration = frame_end - frame_start
                frame_start = frame_end
        # Visual as only image
        else:
            print('no image')
            image_file_path = blender_data['visual']['filePath']
            camera_object = bpy.data.objects['Camera']
            new_camera = duplicateObject(camera_object)
            new_camera.location.x = x_location_cam
            bpy.context.scene.update()

            image_object = createImageAsPlane(image_file_path,
                                              location=(new_camera.location.x, 1.0, new_camera.location.z))
            scale_image_to_fit_frame(new_camera, image_object)
            x_location_cam += 2

            # Create scene strip
            print('frame_end ' + str(frame_end))
            bpy.ops.sequencer.scene_strip_add({'area': area}, frame_start=frame_start)
            active_strip = bpy.context.scene.sequence_editor.active_strip
            print('Strip ')
            print(active_strip)
            active_strip.scene_camera = new_camera
            active_strip.blend_type = 'ALPHA_UNDER'
            active_strip.frame_final_duration = duration_fps
            frame_start = frame_end

        # Create video strip
        # videos = blender_data['video_urls']
        # for video in videos:
        #     bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=video['filePath'],frame_start=frame_start+1)
        #     all_strips = bpy.context.scene.sequence_editor.sequences
        #     video_audio_strip = []
        #     for strip_selected in all_strips:
        #         if strip_selected.select:
        #             video_audio_strip.append(strip_selected)
        #     # Only show 30 s of video
        #     for strip in video_audio_strip:
        #         if strip.frame_final_duration>600:
        #             strip.frame_final_duration = 600
        #     frame_end = frame_start+ 600
        #     frame_start = frame_end

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
