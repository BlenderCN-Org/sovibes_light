import argparse
import json
import os
import urllib

import bpy
import sys
sys.path.append(os.getcwd()+'/')
print(sys.path)
bpy.ops.wm.addon_enable(module="io_import_images_as_planes")
from blender_utils import *

# ---------------------------------------------
# Get only title sentence data
# ---------------------------------------------
def get_title_data(json_data):
    for sentence in json_data:
        if sentence.get('title'):
            return sentence


def initScene(args):
    # try:
    print('INITSCENE START')

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
            title_data = get_title_data(blender_data['audios'])
            print(title_data)
            duration_fps = title_data['title']['duration'] * get_scene_render_fps()
            print('duration fps : ' + str(duration_fps))

            set_scene_frame_end(duration_fps)
            print('set scene frame end complete')
        #Create visual image object
        if blender_data.get('visual'):
            if blender_data['visual'].get('filePath'):
                createImageDummyDuplicate(bpy.data.objects["@visual_dummy"], blender_data['visual']['filePath'])
            print('Visual image added')
    # except:
    #     print('Error initializing scene')

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
    initScene(parser.parse_args())
    renderScene(parser.parse_args())
except ArgumentParserError:
    pass
except SystemExit:
    pass