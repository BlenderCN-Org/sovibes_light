import pyvona
from enum import Enum

class ivonaUsEnglishVoices(Enum):
    Salli = 'Salli'

# Initialize ivona voice
def initYvonaTtsEngine ():

    ivonaVoice = pyvona.create_voice('GDNAJVR7DOF5M332VY3Q','RMlAiEzHBrFdXY0lP7TLjKptE0SjCbBcgEzVPHDz')
    ivonaVoice.voice_name='Salli'
    ivonaVoice._codec='mp3'
    return ivonaVoice

# Text to speech, return the filepath of the tts file
def stringToVoice(string,filePath):
    ivonaVoice = initYvonaTtsEngine()
    try:
        ivonaVoice.fetch_voice(string,filePath)
    except ConnectionError :
        print('Connection error')
        print(ConnectionError.__traceback__)
    return filePath

stringToVoice('Hello world','test.mp3')