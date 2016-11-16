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


def initScene(args):
    # try:
    print('INITSCENE START')

    bpy.ops.object.select_all(action='DESELECT')
    jsonDescriptionFilePath = os.path.abspath(args.input)
    with open(jsonDescriptionFilePath) as blender_data_file:
        blender_data = json.load(blender_data_file)

        # Create source text object
        source = blender_data['origin_title']
        sourceObject = duplicateObject(bpy.data.objects["@source_name_dummy"])
        setTextContent(sourceObject, source)
        bpy.context.scene.update()
        fitTextDimension(sourceObject, bpy.data.objects['@source_bounding_box'])
        sourceObject.hide_render = False

        # Create source visual image object
        if blender_data.get('source_visual'):
            try:
                createImageDummyDuplicate(bpy.data.objects["@source_icon"], blender_data['source_visual'])
            except:
                print('Impossible to create visual icon')

        #Create title text object
        title = blender_data['title']
        title = ''.join(formatString(title, len(bpy.data.objects["@title_dummy"].data.body)))
        try:
            titleObject = duplicateObject(bpy.data.objects["@title_dummy"])
            setTextContent(titleObject, title)
            bpy.context.scene.update()
            fitTextDimension(titleObject, bpy.data.objects['@title_bounding_box'])
            titleObject.hide_render = False
        except:
                print('Duplicate impossible')
    # except:
    #     print('Error initializing scene')

def renderScene(args):
    # Initialize scene/camera
    scene = bpy.context.scene
    # scene.frame_start = 1
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