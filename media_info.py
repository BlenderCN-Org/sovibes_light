import os
import subprocess
from os.path import join

from subprocess import Popen


def create_json_media_info_file(dir_path):
    json_file_path=''
    for file in os.listdir(dir_path):
        file_path = join(dir_path, file)
        if os.path.isfile(file_path):
            cmd = 'mediainfo ' + '"' + file_path + '"'
            p = Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                      close_fds=True)
            output = p.stdout.read()

    return json_file_path