from mutagen.mp3 import MP3
import time

# Return a float
def get_audio_duration(audio_file_path):
    audio = MP3(audio_file_path)
    audio.info
    return audio.info.length

# Return a string
def get_audio_duration_HH_MM_SS(audio_file_path):
    return time.strftime('%H:%M:%S', time.gmtime(get_audio_duration(audio_file_path)))
