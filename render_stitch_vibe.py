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
from ffmpeg_utils import get_video_duration_in_sec


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
        title_data = {}
        scene_render_fps = get_scene_render_fps()
        slide_duration = blender_data['introVibe']['duration'] + blender_data['slideVibe']['duration']
        slide_duration_fps = slide_duration * scene_render_fps
        total_duration = slide_duration
        for video in blender_data['videos']:
            total_duration += video['duration']

        # TODO add outro duration
        total_duration += 4

        total_duration_fps = total_duration * scene_render_fps
        set_scene_frame_end(total_duration_fps)
        scene = bpy.context.scene

        print('SCENE DURATION : '+ str(scene.frame_end))
        # if blender_data.get('audios'):
        #     title_data = get_title_data(blender_data['audios'])
        #     print(title_data)
        #     duration_fps = title_data['title']['duration'] * get_scene_render_fps()
        #     set_scene_frame_end(duration_fps)
        #     # Add sound strip


        # else:
        #     print('No summary impossible to vibesify')
        #     pass

        # Add background audio strip
        print('ADD BACKGROUND AUDIO')
        bpy.ops.sequencer.sound_strip_add({'area': area}, filepath=blender_data['backgroundAudio']['filePath'],
                                          frame_start=0, channel=1)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        active_strip.volume = 0.15
        active_strip.frame_final_duration = slide_duration_fps
        duration = active_strip.frame_final_duration

        # Add intro slideshow movie strip
        print('ADD INTRO')
        bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=blender_data['introVibe']['filePath'],
                                          frame_start=0, channel=2)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        next_frame_start = active_strip.frame_final_duration + 1

        # Add transition
        print('ADD TRANSITION')
        transition_file_path = os.getcwd() + '/blender_elements/Videos/transitions/transition_strips_horizontal.avi'
        transition_duration_fps = get_video_duration_in_sec(transition_file_path) * scene_render_fps
        bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=transition_file_path,
                                          frame_start=next_frame_start - (transition_duration_fps / 2), channel=2)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        active_strip.blend_type = 'ALPHA_OVER'

        # Add slide vibe video
        print('ADD SLIDE')
        bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=blender_data['slideVibe']['filePath'],
                                          frame_start=next_frame_start, channel=2)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        next_frame_start = active_strip.frame_final_duration + next_frame_start + 1

        # Add transition
        print('ADD TRANSITION')
        bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=transition_file_path,
                                          frame_start=next_frame_start - (transition_duration_fps / 2), channel=10)
        active_strip = bpy.context.scene.sequence_editor.active_strip
        active_strip.blend_type = 'ALPHA_OVER'

        # Add videos
        print('ADD VIDEOS')
        for video in blender_data['videos']:
            print('ADD VIDEO')
            bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=video['filePath'],
                                              frame_start=next_frame_start, channel=3)

            active_strip = bpy.context.scene.sequence_editor.active_strip
            scene = bpy.context.scene
            scene.render.fps = 24
            scene.render.fps_base = 1
            for strip in bpy.context.scene.sequence_editor.sequences:
                if strip.select and strip.type == 'SOUND':
                    print('sound strip length : ' + str(strip.frame_final_duration))
                    sound_strip_duration = strip.frame_final_duration
                    strip.select = False
                    ratio_scene = scene.render.resolution_x / scene.render.resolution_y
                    ratio_video = 0
                    if video.get('width') and video.get('height'):
                        ratio_video = video['width'] / video['height']
                    else:
                        print('video ratio from origin')
                        ratio_video = active_strip.elements[0].orig_width/active_strip.elements[0].orig_height
                    if video['frameRate'] != scene_render_fps:
                        print('active strip length : ' + str(active_strip.frame_final_duration))
                        active_strip.frame_final_duration = sound_strip_duration

                        print('ADD EFFECT SPEED')
                        bpy.ops.sequencer.effect_strip_add({'area': area}, type='SPEED',
                                                           frame_start=next_frame_start)
                        print('ADD EFFECT TRANSFORM')
                        bpy.ops.sequencer.effect_strip_add({'area': area}, type='TRANSFORM',
                                                           frame_start=next_frame_start)
                        active_strip = bpy.context.scene.sequence_editor.active_strip

                        if ratio_video > ratio_scene:
                            print('ADD TRANSFORM SCALE Y')
                            active_strip.scale_start_y = (scene.render.resolution_x * video['height']) / (
                            video['width'] * scene.render.resolution_y)
                        elif ratio_video < ratio_scene:
                            print('ADD TRANSFORM SCALE Y')
                            active_strip.scale_start_x = (scene.render.resolution_y * video['width']) / (
                            video['height'] * scene.render.resolution_x)
                        next_frame_start += active_strip.frame_final_duration


                    else:

                        if ratio_video > ratio_scene:
                            print('ADD EFFECT TRANSFORM')
                            bpy.ops.sequencer.effect_strip_add({'area': area}, type='TRANSFORM',
                                                               frame_start=next_frame_start)
                            active_strip = bpy.context.scene.sequence_editor.active_strip
                            print('ADD TRANSFORM SCALE Y')
                            active_strip.scale_start_y = (scene.render.resolution_x * video['height']) / (
                                video['width'] * scene.render.resolution_y)
                        elif ratio_video < ratio_scene:
                            print('ADD EFFECT TRANSFORM')
                            bpy.ops.sequencer.effect_strip_add({'area': area}, type='TRANSFORM',
                                                               frame_start=next_frame_start)
                            active_strip = bpy.context.scene.sequence_editor.active_strip
                            print('ADD TRANSFORM SCALE Y')
                            active_strip.scale_start_x = (scene.render.resolution_y * video['width']) / (
                                video['height'] * scene.render.resolution_x)

                        next_frame_start += active_strip.frame_final_duration
                    break
            print('ADD TRANSITION')
            bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=transition_file_path,
                                              frame_start=next_frame_start - (transition_duration_fps / 2),
                                              channel=10)
            active_strip = bpy.context.scene.sequence_editor.active_strip
            active_strip.blend_type = 'ALPHA_OVER'
        print('ADD OUTRO')
        # outro_file_path = os.getcwd() + '/blender_elements/Videos/outro/outro_vertical.mp4'
        # bpy.ops.sequencer.movie_strip_add({'area': area}, filepath=outro_file_path,
        #                                   frame_start=next_frame_start,
        #                                   channel=2)
    # except:
    #     print('Impossible to init slideshow scene')
    pass


def renderScene(args):
    # Initialize scene/camera
    scene = bpy.context.scene
    scene.frame_start = 1
    # scene.frame_end = args.fps * args.time
    # scene.render.image_settings.file_format = args.file_format
    # scene.render.ffmpeg.codec = args.codec
    # scene.render.ffmpeg.format = args.format
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
