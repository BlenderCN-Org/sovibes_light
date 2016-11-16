



def get_video_info(file_path):
    p = subprocess.Popen(['mediainfo', '-i', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_video_width(file_path):
    pass

def get_video_height(file_path):
    pass