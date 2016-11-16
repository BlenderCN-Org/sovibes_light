import bpy
import os
import datetime

import math


def get_scene_render_fps():
    scene = bpy.context.scene
    return scene.render.fps


def set_scene_frame_end(frame_end):
    scene = bpy.context.scene
    scene.frame_end = frame_end

def get_scene_frame_end():
    return bpy.context.scene.frame_end


def find_sequence_editor_area():
    screens = [bpy.context.screen] + list(bpy.data.screens)
    for screen in screens:
        for area in screen.areas:
            if area.type == 'SEQUENCE_EDITOR':
                return area


def add_list_sound_strip(file_path_list, framestart):
    area = find_sequence_editor_area()
    fps = get_scene_render_fps()
    print(fps)
    for file in file_path_list:
        bpy.ops.sequencer.sound_strip_add({'area': area}, filepath=file['filepath'], frame_start=framestart)
        framestart = math.ceil(file['duration'] * fps)
        print(framestart)

def get_scale_ratio(object):
    return object.scale.x/object.scale.y

def move_object_keyframes(frame_start, frame_end, object):
    object_anim_data = object.animation_data
    print('move object')
    for fcurve in object_anim_data.action.fcurves:
        print(fcurve)
        print(fcurve.keyframe_points)
        if len(fcurve.keyframe_points) >= 4:
            print('fcurve')
            for keyframe in fcurve.keyframe_points[:len(fcurve.keyframe_points)-2]:
                keyframe.co[0] += frame_start
            delta_keyframe = fcurve.keyframe_points[3].co[0] - fcurve.keyframe_points[2].co[0]
            print('delta keyframe = ' +str(delta_keyframe))
            fcurve.keyframe_points[-2:][1].co[0] = frame_end
            fcurve.keyframe_points[-2:][0].co[0] = frame_end - delta_keyframe
        else:
            print('fcurveelse')
            for keyframe in fcurve.keyframe_points:
                keyframe.co[0] += frame_start

    pass


# Set a material to a blender object
def setMaterial(object, material):
    objectData = object.data
    objectData.materials.append(material)


# Create text object with parameters : text,location,scale and material
# TODO: add rotation parameter
def createText(string, location, scale):
    bpy.ops.object.text_add(enter_editmode=True, location=location, rotation=(1.5708, 0, 0))
    bpy.ops.font.delete()
    bpy.ops.font.text_insert(text=string)
    bpy.ops.object.editmode_toggle()
    textObject = bpy.context.active_object
    textObject.scale = scale
    return textObject


# Create image as plane object
# TODO: add rotation parameter
def createImageAsPlane(imageFilePath, location=(0, 0, 0), scale=(1, 1, 1)):
    if os.path.exists(imageFilePath):
        bpy.ops.import_image.to_plane(alpha_mode='STRAIGHT', use_shadeless=True,
                                      files=[{'name': os.path.abspath(imageFilePath)}],
                                      directory=os.path.dirname(imageFilePath))
        imageObject = bpy.context.active_object
        imageObject.rotation_euler = [1.5708, 0, 0]
        imageObject.location = location
        imageObject.scale = scale
        return imageObject


# Animate object
def animateTranslateObject(blenderObject, frameAnimationStart, frameAnimationEnd, finalLocation):
    blenderObject.keyframe_insert(data_path="location", frame=frameAnimationStart)
    blenderObject.location = finalLocation
    blenderObject.keyframe_insert(data_path="location", frame=frameAnimationEnd)


# Duplicate Object
def duplicateObject(textObjectCopy):
    try:
        bpy.ops.object.select_all(action='DESELECT')
        textObjectCopy.select = True
        print(textObjectCopy.name)
        bpy.ops.object.duplicate()
        # TODO Very Ugly manner change that in the nearest future
        newObject = bpy.context.selected_objects[0]
        return newObject
    except:
        print('Impossible to duplicate object')


# Rescale ojbect to XYRatio
def scaleXYRatioObject(object, XYratio):
    actualXYratio = object.scale.x / object.scale.y
    if actualXYratio < XYratio:
        object.scale.y = object.scale.x * XYratio
    else:
        object.scale.x = object.scale.y * XYratio


# Duplicate location data
def duplicateLocation(objectSource, objectDestination):
    objectDestination.location = objectSource.location


# duplicate scale data
def duplicateScale(objectSource, objectDestination):
    objectDestination.scale = objectSource.scale


# Copy animation from object source to object destination
def duplicateAnimation(objectSource, objectDestination):
    sourceAnimationData = objectSource.animation_data
    properties = [property.identifier for property in sourceAnimationData.bl_rna.properties if not property.is_readonly]

    if objectDestination.animation_data == None:
        objectDestination.animation_data_create()
    for prop in properties:
        setattr(objectDestination.animation_data, prop, getattr(sourceAnimationData, prop))


# Create image and duplicate location, scale and animation
def createImageDummyDuplicate(object, imageFilePath):
    imageObject = createImageAsPlane(imageFilePath)
    duplicateLocation(object, imageObject)
    duplicateScale(object, imageObject)
    duplicateAnimation(object, imageObject)

def get_plane_ratio(plane_object):
    return plane_object.dimensions.x/plane_object.dimensions.y
#################################################################################################
#                                           TEXT FUNCTIONS                                      #
#################################################################################################

# Check if text object dimension fits in dummy object dimension
def checkTextDimensionX(textObject, dummyObject):
    if textObject.dimensions.x > dummyObject.dimensions.x:
        return True
    else:
        return False


# Check if text object dimension fits in dummy object dimension
def checkTextDimensionY(textObject, dummyObject):
    if textObject.dimensions.y > dummyObject.dimensions.y:
        return True
    else:
        return False


# Fit text object to the bounding box of the dummy object
def fitTextDimension(textObject, dummyObject):
    # Text object ratio to be used when downscaling or upscaling
    textXYRatio = textObject.scale.x / textObject.scale.y
    if checkTextDimensionX(textObject, dummyObject):
        # if the x dimension of the text object (width) doesn't fit the dummy object, rescale text object
        textObject.dimensions = (dummyObject.dimensions.x, textObject.dimensions.y, textObject.dimensions.z)
        scaleXYRatioObject(textObject, textXYRatio)

    if checkTextDimensionY(textObject, dummyObject):
        # if the y dimension of the text object (height) doesn't fit the dummy object, rescale text object
        textObject.dimensions.y = dummyObject.dimensions.y
        scaleXYRatioObject(textObject, textXYRatio)
    return True


# Set text content
def setTextContent(textObject, content):
    try:
        textObject.data.body = content
        return True
    except:
        print('error')
        return False


# Get text length
def getLengthText(textObject):
    return len(textObject.data.body)


# Return string with each line of lenLineMax
def formatString(string, lenLineMax):
    splitString = string.split()
    lenSplitString = splitString.__len__()
    len = 0
    for n in range(0, lenSplitString - 1):
        splitString[n] += ' '
        len += splitString[n].__len__()
        if (len > lenLineMax):
            splitString[n - 1] += "\n"
            len = splitString[n].__len__()

    return splitString
