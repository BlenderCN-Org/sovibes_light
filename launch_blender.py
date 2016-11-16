import subprocess

print(
    'blender /home/belgaloo/PycharmProjects/sovibes_light/blender_elements/blender_files/slideshow/pattern_slideshow_vertical_1.blend '
    '-P render_slideshow.py '
    '-- ' + '"/home/belgaloo/PycharmProjects/sovibes_light/vibe_workspace/vibes/Donald Trump Tax Records Show He Could Have Avoided Taxes for Nearly Two Decades, The Times Found/description_file.json" '
            '--output /home/belgaloo/PycharmProjects/sovibes_light/vibe.mp4')
try:
    subprocess.call('blender /home/belgaloo/PycharmProjects/sovibes_light/blender_elements/blender_files/intro/intro_blend.blend  '
                    '-P render_stitch_vibe.py '
                    '-- '+'"/home/belgaloo/PycharmProjects/sovibes_light/vibe_workspace/vibes/How the team behind Titanfall 2 built a titan you’ll actually care about/description_file.json" '
                          '--output /home/belgaloo/PycharmProjects/sovibes_light/vibe.mp4',shell=True)

except:
    pass